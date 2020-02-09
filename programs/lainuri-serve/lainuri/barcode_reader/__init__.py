from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

import serial
import time
import _thread as thread
import json
import importlib

import lainuri.helpers
import lainuri.barcode_reader.model.WGC300UsbAT as WGC300UsbAT
import lainuri.barcode_reader.model.WGI3220USB as WGI3220USB


class BarcodeReader():
  def __init__(self):
    self.model = get_config('devices.barcode-reader.model')

    try:
      self.config_module = importlib.import_module(f'.{self.model}', 'lainuri.barcode_reader.model')
    except ModuleNotFoundError as e:
      raise Exception(f"Unknown barcode reader model '{self.model}'!")

    self.serial: serial.Serial = self.connect_serial()
    self.autoconfigure()

  def connect_serial(self) -> serial.Serial:
    log.info(f"Connecting to '{self.model}'")
    return self.config_module.connect(self)

  def autoconfigure(self):
    log.info(f"Autoconfiguring '{self.model}'")
    self.config_module.autoconfigure(self)

  def is_connected(self):
    self.config_module.is_connected(self)

  def write(self, cmd):
    log.info(f"WRITE--> {type(cmd)}")
    data = cmd.pack()
    for b in data: print(hex(b), ' ', end='')
    print()
    rv = self.serial.write(data)
    log.info(f"-->WRITE {type(cmd)} '{rv}'")
    return rv

  def read(self):
    self.is_connected() # The serial connection can break during a long-running process, so reconnect if needed
    rv = b''
    self.serial.timeout = 0 # non-blocking mode, just read whatever is in the buffer
    while self.serial.in_waiting:
      rv = rv + self.serial.read(255)
    return rv

  def blocking_read(self):
    # Use the serial-system's blocking read to notify us of new bytes to read, instead of looping and polling.
    self.serial.timeout = None # wait forever / until requested number of bytes are received
    rv = self.serial.read(1)
    rv = rv + self.read()
    if (rv):
      barcode = rv[0:-1].decode('latin1') # Pop the last character, as it it the barcode termination character
      log.info(f"Received barcode='{barcode}' bytes='{rv}'")
      return barcode

  def start_polling_barcodes(self, handler):
    """
    Forks a thread to poll the serial connection for barcodes.
    Turns the read barcodes into push notifications.
    """
    thread.start_new_thread(self.polling_barcodes_thread, (handler, True))

  def polling_barcodes_thread(self, handler, dummy):
    log.info("Barcodes polling starting")

    while(1):
      barcode = self.blocking_read()
      if (barcode):
        handler(barcode)

    log.info(f"Terminating WGC300 thread")