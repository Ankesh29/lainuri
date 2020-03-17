from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)
# Save HTTP responses to a scrape-log so we can later inspect what went wrong in the brittle screen scraping components.
log_scrape = logging.getLogger('lainuri.scraping')

from lainuri.constants import Status
import lainuri.exception as exception
import lainuri.exception.ils as exception_ils

import lainuri.websocket_handlers.status

from bs4 import BeautifulSoup
import bs4
import functools
import json
from pprint import pprint
import re
import time
import traceback
import urllib3
import urllib3.exceptions


class KohaAPI():
  required_permissions = {
    'auth': 'get_session',
    'borrowers': 'view_borrowers',
  #  'catalogue': 'staff_login',
    'circulate': 'circulate_remaining_permissions',
    'editcatalogue': '*',
  }

  sessionid = ''
  koha_baseurl = ''
  current_event_id = ''
  current_request_url = ''
  reauthenticate_tries = 0

  def __init__(self):
    self.koha_baseurl = get_config('koha.baseurl')
    self.http = urllib3.PoolManager(
      timeout=urllib3.Timeout(connect=get_config('server.timeout_request_connect_ms')/1000, read=get_config('server.timeout_request_read_ms')/1000),
      retries=False,
    )

  def _request(self, method, url, fields=None, headers=None):
    try:
      for i in range(1,4):
        r = self.http.request(
          method,
          url,
          fields,
          headers,
        )
        lainuri.websocket_handlers.status.set_ils_connection_status(Status.SUCCESS)
        return r
    except Exception as e:
      if isinstance(e, urllib3.exceptions.NewConnectionError):
        lainuri.websocket_handlers.status.set_ils_connection_status(Status.ERROR)
        time.sleep(1)
      elif isinstance(e, urllib3.exceptions.ConnectTimeoutError):
        lainuri.websocket_handlers.status.set_ils_connection_status(Status.PENDING)
        time.sleep(1)
      else:
        lainuri.websocket_handlers.status.set_ils_connection_status(Status.ERROR)
        raise e

  def _scrape_log_header(self, r: urllib3.HTTPResponse):
    return f"event_id='{self.current_event_id}' status='{r.status} url='{r.geturl() or self.current_request_url}"

  def _receive_json(self, r: urllib3.HTTPResponse):
    data = r.data.decode('utf-8')
    log_scrape.info(self._scrape_log_header(r) + "\n" + data)
    payload = json.loads(data)
    self._maybe_not_logged_in(r, payload)
    self._maybe_missing_permission(payload)
    return payload

  def _receive_html(self, r: urllib3.HTTPResponse) -> (BeautifulSoup, list, list):
    data = r.data.decode('utf-8')
    try:
      soup = BeautifulSoup(data, features="html.parser")
      for e in soup.select('script'): e.decompose() # Remove all script-tags
      log_scrape.info(self._scrape_log_header(r) + "\n" + soup.select_one('body').prettify())

      alerts = soup.select('.dialog.alert')
      # Filter away hidden alerts
      alerts = [m.prettify() for m in alerts if not(m.attrs.get('style')) or not(re.match(r'(?i:display:\s*none)', m.attrs.get('style')))]
      messages = soup.select('.dialog.message')
      # Filter away hidden messages
      messages = [m.prettify() for m in messages if not(m.attrs.get('style')) or not(re.match(r'(?i:display:\s*none)', m.attrs.get('style')))]
    except Exception as e:
      log_scrape.info(f"event_id='{self.current_event_id}'\n" + data)
      log.error(f"Failed to parse HTML for event_id='{self.current_event_id}': {traceback.format_exc()}")
      raise e

    self._maybe_not_logged_in(r, soup)
    return (soup, alerts, messages)

  def _maybe_not_logged_in(self, r, payload):
    if isinstance(payload, dict) and payload.get('error', None):
      if r.status == 401:
        self.reauthenticate_tries += 1
    elif isinstance(payload, BeautifulSoup):
      login_error = payload.select("#login_error")
      if login_error:
        self.reauthenticate_tries += 1

    if self.reauthenticate_tries == 2:
      if not self.authenticate():
        self.reauthenticate_tries = 0
        raise Exception(f"Lainuri device was not authenticated to Koha and failed to automatically reauthenticate.")
      self.reauthenticate_tries = 0

  def _maybe_missing_permission(self, payload):
    if isinstance(payload, dict) and payload.get('error', None):
      if payload.get('required_permissions'):
        raise Exception(f"Lainuri device is missing permission '{payload.get('required_permissions')}'. Lainuri needs these permissions to access Koha: '{self.required_permissions}'")

  def authenticated(self):
    r = self.request(
      'GET',
      self.koha_baseurl+'/api/v1/auth/session',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      }
    )
    self._receive_json(r)
    if r.status == '200':
      return 1
    else:
      return 0

  def authenticate(self):
    log.info(f"Authenticating. Reauth '{self.reauthenticate_tries}'")
    self.reauthenticate_tries += 1
    r = self._auth_post(userid=get_config('koha.userid'), password=get_config('koha.password'))
    payload = self._receive_json(r)
    error = payload.get('error', None)
    if error:
      if 'Login failed' in error: raise exception_ils.InvalidUser(get_config('koha.userid'))
      else: raise Exception(f"Unknown error '{error}'")
    self.sessionid = payload['sessionid']
    self.reauthenticate_tries = 0
    return payload

  def authenticate_user(self, user_barcode, userid=None, password=None) -> dict:
    log.info(f"Auth user '{user_barcode or userid}'.")
    if password == None:
      borrower = self.get_borrower(user_barcode=user_barcode)
      if borrower:
        return borrower
      else:
        raise exception_ils.InvalidUser(user_barcode)

  def _auth_post(self, password, userid=None, user_barcode=None):
    if not userid or user_barcode:
      raise Exception("Mandatory parameter 'userid' or 'user_barcode' is missing!")
    fields = {
      'password': password,
    }
    if userid: fields['userid'] = userid
    if user_barcode: fields['user_barcode'] = user_barcode

    return self.http.request(
      'POST',
      self.koha_baseurl + '/api/v1/auth/session',
      fields = fields,
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_borrower(self, user_barcode):
    log.info(f"Get borrower: user_barcode='{user_barcode}'")
    r = self.http.request_encode_url(
      'GET',
      self.koha_baseurl + f'/api/v1/patrons',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'cardnumber': user_barcode,
      },
    )
    self.current_request_url = self.koha_baseurl + f'/api/v1/patrons'
    payload = self._receive_json(r)
    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")

    if len(payload) > 1:
      raise Exception(f"Got more than one user with barcode='{user_barcode}'!")
    if len(payload) == 0:
      raise exception_ils.NoUser(user_barcode)

    return payload[0]

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_item(self, item_barcode):
    log.info(f"Get item: item_barcode='{item_barcode}'")
    r = self.http.request_encode_url(
      'GET',
      self.koha_baseurl + f'/api/v1/items',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
      fields = {
        'barcode': item_barcode,
      },
    )
    self.current_request_url = self.koha_baseurl + f'/api/v1/items'
    payload = self._receive_json(r)
    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")

    if len(payload) > 1:
      raise Exception(f"Got more than one item with item_barcode='{item_barcode}'!")
    if len(payload) == 0:
      raise exception_ils.NoItem(item_barcode)

    return payload[0]

  @functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
  def get_record(self, biblionumber):
    log.info(f"Get record: biblionumber='{biblionumber}'")
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/api/v1/records/{biblionumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    payload = self._receive_json(r)
    error = payload.get('error', None)
    if error:
      if r.status == 404:
        raise exception.NoResults(biblionumber)
      raise Exception(f"Unknown error '{error}'")
    return payload

  def checkin(self, barcode) -> tuple:
    log.info(f"Checkin: barcode='{barcode}'")
    r = self.http.request(
      'POST',
      self.koha_baseurl + '/cgi-bin/koha/circ/returns.pl',
      fields={
        'barcode': barcode
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid};KohaOpacLanguage=en',
      },
    )

    (soup, alerts, messages) = self._receive_html(r)

    states = {}
    alerts = [a for a in alerts if not self.checkin_has_status(a, states, barcode)]
    messages = [a for a in messages if not self.checkin_has_status(a, states, barcode)]

    if (alerts or messages):
      states['unhandled'] = [*(alerts or []), *(messages or [])]
      states['status'] = Status.ERROR
    if states.get('status', None) != Status.ERROR:
      states['status'] = Status.SUCCESS
    log.info(f"Checkin barcode='{barcode}' with states='{states}'")
    return (states.pop('status'), states)

  def checkin_has_status(self, message, states, barcode):
    m_not_checked_out = re.compile('Not checked out', re.S | re.M)
    match = m_not_checked_out.search(message)
    if match:
      states['not_checked_out'] = 1
      return 'not_checked_out'

    m_return_to_another_branch = re.compile('Please return item to: (?P<branchname>.+?)\n', re.S | re.M)
    match = m_return_to_another_branch.search(message)
    if match:
      states['return_to_another_branch'] = match.group('branchname')
      return 'return_to_another_branch'

    m_no_item = re.compile('No item with barcode', re.S | re.M)
    match = m_no_item.search(message)
    if match:
      raise exception_ils.NoItem(barcode)

    return None

  def checkout(self, barcode, borrowernumber) -> tuple:
    log.info(f"Checkout: barcode='{barcode}' borrowernumber='{borrowernumber}'")
    r = self.http.request(
      'POST',
      self.koha_baseurl + '/cgi-bin/koha/circ/circulation.pl',
      fields={
        'restoreduedatespec': '',
        'barcode': barcode,
        'duedatespec': '',
        'borrowernumber': borrowernumber,
        'branch': get_config('koha.branchcode'),
        'debt_confirmed': 0,
      },
      headers = {
        'Cookie': f'CGISESSID={self.sessionid};KohaOpacLanguage=en',
      },
    )
    (soup, alerts, messages) = self._receive_html(r)

    states = {}
    alerts = [a for a in alerts if not self.checkout_has_status(a, states)]
    messages = [a for a in messages if not self.checkout_has_status(a, states)]

    if (alerts or messages):
      states['unhandled'] = [*(alerts or []), *(messages or [])]
      states['status'] = Status.ERROR
    if states.get('status', None) != Status.ERROR:
      states['status'] = Status.SUCCESS
    log.info(f"Checkout complete: barcode='{barcode}' borrowernumber='{borrowernumber}' with states='{states}'")
    return (states.pop('status'), states)

  def checkout_has_status(self, message, states):
    m_not_checked_out = re.compile('Not checked out', re.S | re.M | re.I)
    match = m_not_checked_out.search(message)
    if match:
      states['not_checked_out'] = 1
      return 'not_checked_out'

    m_needsconfirmation = re.compile('circ_needsconfirmation', re.S | re.M | re.I)
    match = m_needsconfirmation.search(message)
    if match:
      states['needs_confirmation'] = 1
      states['status'] = Status.ERROR
      return 'needs_confirmation'

    return None

  def receipt(self, borrowernumber, slip_type, locale) -> str:
    log.info(f"Receipt: borrowernumber='{borrowernumber}' slip_type='{slip_type}' locale='{locale}'")
    if slip_type not in ['qslip','checkinslip']:
      raise TypeError(f"Receipt:> borrowernumber='{borrowernumber}' slip_type='{slip_type}' locale='{locale}' has invalid slip_type. Allowed values ['qslip','checkinslip']")

    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/cgi-bin/koha/members/printslip.pl?borrowernumber={borrowernumber}&print={slip_type}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid};KohaOpacLanguage={locale}',
      },
    )
    (soup, alerts, messages) = self._receive_html(r)
    if (alerts or messages):
      raise Exception(f"Checkin failed: alerts='{alerts // []}' messages='{messages // []}'")
    receipt = soup.select('#receipt')
    if not receipt:
      raise Exception("Fetching the checkout receipt failed: CSS selector '#receipt' didn't match.")
    if receipt: receipt = receipt[0]
    receipt_text = receipt.prettify()
    return receipt_text

  def availability(self, borrowernumber, itemnumber):
    log.info(f"Availability: borrowernumber='{borrowernumber}' itemnumber='{itemnumber}'")
    r = self.http.request(
      'GET',
      self.koha_baseurl + f'/api/v1/availability/item/checkout?itemnumber={itemnumber}&borrowernumber={borrowernumber}',
      headers = {
        'Cookie': f'CGISESSID={self.sessionid}',
      },
    )
    payload = self._receive_json(r)
    if isinstance(payload, dict) and payload.get('error', None):
      error = payload.get('error', None)
      if error:
        raise Exception(f"Unknown error '{error}'")

    if len(payload) > 1:
      raise Exception(f"Got more than one availability result with borrowernumber='{borrowernumber}' itemnumber='{itemnumber}'!")
    if len(payload) == 0:
      raise Exception(f"Got no availability result with borrowernumber='{borrowernumber}' itemnumber='{itemnumber}'!")

    return payload[0]['availability']


class MARCRecord():
  candidate_author_fields = {'100': ['a'], '110': ['a']}
  candidate_title_fields  = {'245': ['a'], '240': ['a']}
  candidate_book_cover_url_fields  = {'856': ['u']}
  candidate_edition_fields = {'250': ['a']}

  _author = ''
  _title = ''
  _book_cover_url = ''
  _edition = ''

  def __init__(self, record_xml):
    if isinstance(record_xml, str):
      self.soup = BeautifulSoup(record_xml, "xml")
    else:
      self.soup = BeautifulSoup(record_xml['marcxml'], "xml")

  def author(self):
    if self._author: return self._author
    for field_code in self.candidate_author_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_author_fields[field_code]:
            self._author = sf.get_text()
            return self._author

  def title(self):
    if self._title: return self._title
    for field_code in self.candidate_title_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_title_fields[field_code]:
            self._title = sf.get_text()
            return self._title

  def book_cover_url(self):
    if self._book_cover_url: return self._book_cover_url
    for field_code in self.candidate_book_cover_url_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_book_cover_url_fields[field_code]:
            self._book_cover_url = sf.get_text()
            return self._book_cover_url

  def edition(self):
    if self._edition: return self._edition
    for field_code in self.candidate_edition_fields:
      field = self.soup.select_one(f'datafield[tag="{field_code}"]')
      if field:
        for sf in field.children:
          if isinstance(sf, bs4.element.Tag) and sf.attrs['code'] in self.candidate_edition_fields[field_code]:
            self._author = sf.get_text()
            return self._author


@functools.lru_cache(maxsize=get_config('koha.api_memoize_cache_size'), typed=False)
def get_fleshed_item_record(barcode):
  log.info(f"Get fleshed item record: barcode='{barcode}'")
  exception = None
  try:
    if not barcode: raise exception_ils.NoItemIdentifier()
    item = koha_api.get_item(barcode)
    payload = koha_api.get_record(item['biblionumber'])
    record = MARCRecord(payload)

    return {
      'author': record.author(),
      'title': record.title(),
      'book_cover_url': record.book_cover_url(),
      'edition': record.edition(),
      'item_barcode': barcode,
      'status': Status.SUCCESS,
    }
  except Exception as e:
    exception = {
      'type': type(e).__name__,
      'trace': traceback.format_exc(),
    }

  return {
    'item_barcode': barcode,
    'status': Status.ERROR,
    'states': {
      'exception': exception,
    },
  }


# TODO: Thread safety for KohaAPI()
koha_api = KohaAPI()
