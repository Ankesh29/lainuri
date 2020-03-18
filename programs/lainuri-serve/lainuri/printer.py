from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from jinja2 import Template
from datetime import datetime
import os
import time
import traceback
from weasyprint import HTML, CSS
import subprocess

cli_print_command = ['lp', '-']

def print_html(html_text: str, page_increment: int = 10, css_dict: dict = None):
  """
  page_increment: Granularity to look for the minimum height of the document to fit all the content. the bigger the faster, but more paper is wasted with trailing margin.

  css_dict: Overload config.yaml's 'devices.thermal-printer.css' with this. Mostly useful for testing.
  """
  log.debug(f"print_html text='{html_text}'")
  start_time = time.time()

  weasy_html = HTML(string=html_text)

  pages = 100
  heigth = 25 # Keep looping to find the correct page size to fit all the content
  i = 0
  while pages != 1:
    i += 1
    default_css = CSS(string=' \
      body {\
        width: 72mm;\
        font-size: 12px;\
        border: solid 2px;\
        margin: 0px;\
        padding: 0px;\
      }\
      @page {\
        size: 72mm '+str(heigth)+'mm;\
        margin: 0px;\
        padding: 0px;\
      }\
    ')
    doc = weasy_html.render(
      stylesheets=[default_css, *[CSS(string=css) for css in format_css_rules_from_config(css_dict)]],
      enable_hinting = True,
      presentational_hints = True,
    )
    pages = len(doc.pages)

    old_height = heigth
    if i == 1: heigth = heigth * pages
    else: heigth = heigth + (page_increment * (pages-1))
    log.debug(f"Sampling to fit content on one document: i='{i}', old_height='{old_height}', pages='{pages}', new height='{heigth}'")

  end_time = time.time()
  log.info(f"print_html():> pages='{len(doc.pages)}', page_increment='{page_increment}px', html processing runtime='{end_time - start_time}s' iterations='{i}' page0='{doc.pages and doc.pages[0].__dict__}'")

  print_thermal_receipt(doc.write_pdf())

  return 1

def format_css_rules_from_config(css_dict: dict = None):
  if not css_dict: css_dict = get_config('devices.thermal-printer.css')
  if not css_dict: return []

  css = "body {\n"
  for css_directive, value in css_dict.items():
    if value[-1] != ';': value += ';'
    css += f"  {css_directive}: {value}\n"
  css += "}\n"

  css_string = get_config('devices.thermal-printer.css_string')
  return [stylesheet for stylesheet in [css, css_string] if stylesheet]

def print_thermal_receipt(byttes: bytes):
  global cli_print_command
  ## Save to log the receipt document
  open(
    os.environ.get('LAINURI_LOG_DIR')+'receipt'+datetime.today().isoformat()+'.pdf',
    'wb',
  ).write(byttes)

  ## Invoke system CUPS printer
  if get_config('devices.thermal-printer.enabled'):
    process = subprocess.Popen(cli_print_command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(input=byttes, timeout=20)
    if process.returncode != 0:
      raise Exception(f"Program exit code not 0. exit='{process.returncode}', stderr='{process.stderr}', stdout='{process.stdout}', command='{cli_print_command}'")

  else:
    log.info(f"Thermal printer is disabled from configuration.")

def get_sheet(receipt_template_name: str, items: list, borrower: dict, header: str = None, footer: str = None) -> str:
  receipt_template = open(
    os.environ.get('LAINURI_CONF_DIR')+'/'+receipt_template_name,
    'r',
  ).read()
  return render_jinja2_template(receipt_template=receipt_template, items=items, borrower=borrower, header=header, footer=footer)

def render_jinja2_template(receipt_template: str, items: list, borrower: dict, header: str = None, footer: str = None):
  return Template(receipt_template).render(
    items=items,
    borrower=borrower,
    today=datetime.today().strftime(get_config('dateformat')),
    header=header,
    footer=footer,
  )
