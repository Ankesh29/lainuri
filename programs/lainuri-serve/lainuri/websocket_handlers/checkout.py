from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

from lainuri.constants import Status
import lainuri.db.transaction_history
import lainuri.event
import lainuri.event_queue
import lainuri.exception as exception
import lainuri.exception.ils as exception_ils
from lainuri.koha_api import koha_api
import lainuri.rfid_reader as rfid


def checkout(event):
  availability = None
  status = None
  states = None
  try:
    # Get the borrower
    borrower = koha_api.get_borrower(user_barcode=event.user_barcode)

    # Get the itemnumber
    item = koha_api.get_item(event.item_barcode)

    # Get curated availability from the REST API. This doesn't say if the item could be checked out from this specific branch
    # but it is way better at communicating the small details.
    availability = koha_api.availability(itemnumber=item['itemnumber'], borrowernumber=borrower['borrowernumber'])
    if availability['available'] != True:
      lainuri.event_queue.push_event(
        lainuri.event.LECheckOutComplete(
          item_barcode=item['barcode'],
          user_barcode=borrower['cardnumber'],
          tag_type=event.tag_type,
          status=Status.ERROR,
          states=_merge_availability_to_states(availability, {})
        )
      )
      return

    status = _check_availability_statuses(availability)
    if status == None:
      # Checkout to Koha
      (status, states) = koha_api.checkout(event.item_barcode, borrower['borrowernumber'])

    if status == Status.SUCCESS: lainuri.db.transaction_history.post({'transaction_type': 'checkout', 'borrower_barcode': event.user_barcode, 'item_barcode': event.item_barcode})

    lainuri.event_queue.push_event(
      lainuri.event.LECheckOutComplete(
        item_barcode=event.item_barcode,
        user_barcode=borrower['cardnumber'],
        tag_type=event.tag_type,
        status=status,
        states=_merge_availability_to_states(availability, states),
      )
    )

  except Exception as e:
    log.exception(f"Exception at {__name__}")
    lainuri.event_queue.push_event(
      lainuri.event.LECheckOutComplete(
        item_barcode=event.item_barcode,
        user_barcode=event.user_barcode,
        tag_type=event.tag_type,
        status=Status.ERROR,
        states=_merge_availability_to_states(availability or {}, {'exception': {
          'type': type(e).__name__,
          'trace': str(e)}
        }),
      )
    )
    return

def _check_availability_statuses(availability):
  status = None
  confirmations = availability.get('confirmations', None)
  # if availability.confirmations?.Checkout::Renew
  if confirmations and confirmations.get("Checkout::Renew", None) != None: # Sorry for Pythonisms
    # Skip renewing the Item because it is already checked out to this patron
    status = Status.SUCCESS if availability['available'] else Status.ERROR
  elif confirmations and confirmations.get("Item::Held", {}).get("status", None) == "Waiting":
    # A hold is already caught and waiting on shelf, block checkout
    status = Status.ERROR
    confirmations["Item::Held::Waiting"] = True
  return status

def _merge_availability_to_states(availability, states):
  merged = {}
  if availability.get('confirmations', None):
    for v in availability['confirmations']:
      merged[v] = True
  if availability.get('notes', None):
    for v in availability['notes']:
      merged[v] = True
  if availability.get('unavailabilities', None):
    for v in availability['unavailabilities']:
      merged[v] = True
  if not states: return merged
  return {**states, **merged}
