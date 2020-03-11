#!/usr/bin/python3

import context

import sys
import time
import unittest.mock

import lainuri.barcode_reader
from lainuri.barcode_reader.model.WGC_commands import *
import lainuri.exception

thread_wait_sleep = 0.5

def tezt_manually_barcode_reader():
  bcr = lainuri.barcode_reader.get_BarcodeReader()

  print("Manually read a barcode now:", file=sys.stderr)
  barcode = bcr.blocking_read()

  assert barcode == ''

def test_barcode_reader_polling_loop(subtests):
  barcode_read_handler_mock = None
  barcode_blocking_read_mock = None
  patcher = None
  thread = None
  bcr = None

  with subtests.test("Given a mocked barcode reader"):
    barcode_read_handler_mock = unittest.mock.Mock()
    patcher = unittest.mock.patch.object(lainuri.barcode_reader.BarcodeReader, 'read_barcode_blocking')
    barcode_blocking_read_mock = patcher.start()
    barcode_blocking_read_mock.return_value = 'mocked-barcode-read'

    bcr = lainuri.barcode_reader.get_BarcodeReader()

  with subtests.test("When the barcode polling starts"):
    thread = bcr.start_polling_barcodes(barcode_read_handler_mock)
    assert thread
    assert poll_thread_is_alive(True, thread)
    time.sleep(thread_wait_sleep)

  with subtests.test("And a barcode is read"):
    barcode_blocking_read_mock.assert_called()

  with subtests.test("Then the handler is called with the read barcode"):
    barcode_read_handler_mock.assert_called_with('mocked-barcode-read')

  with subtests.test("Finally the polling thread is terminated"):
    bcr.stop_polling_barcodes()
    assert poll_thread_is_alive(False, thread)

def test_barcode_reader_polling_loop_exception_handling(subtests, caplog):
  barcode_read_handler_mock = None
  barcode_blocking_read_mock = None
  patcher = None
  thread = None
  bcr = None

  with subtests.test("Given a mocked barcode reader that has a crashing handler"):
    barcode_read_handler_mock = unittest.mock.Mock(side_effect=lainuri.exception.ILS())
    patcher = unittest.mock.patch.object(lainuri.barcode_reader.BarcodeReader, 'read_barcode_blocking')
    barcode_blocking_read_mock = patcher.start()
    barcode_blocking_read_mock.return_value = 'mocked-barcode-read'

    bcr = lainuri.barcode_reader.get_BarcodeReader()

  with subtests.test("When the barcode polling starts"):
    thread = bcr.start_polling_barcodes(barcode_read_handler_mock)
    assert thread
    assert poll_thread_is_alive(True, thread)
    time.sleep(thread_wait_sleep)

  with subtests.test("And a barcode is read"):
    barcode_blocking_read_mock.assert_called()

  with subtests.test("Then the handler is called with the read barcode"):
    barcode_read_handler_mock.assert_called_with('mocked-barcode-read')

  with subtests.test("And the polling thread captures the exception"):
    assert 'lainuri.exception.ILS' in ' '.join([''.join(str(t)) for t in caplog.record_tuples])

  with subtests.test("And the polling thread endures the Exception and keeps on polling"):
    time.sleep(thread_wait_sleep) # Give some time to die
    assert thread.is_alive()

  with subtests.test("Finally the polling thread is terminated"):
    bcr.stop_polling_barcodes()
    assert poll_thread_is_alive(False, thread)


def poll_thread_is_alive(is_alive: bool, thread):
  count = 20
  while(thread.is_alive() != is_alive):
    count -= 1
    time.sleep(0.1)
    if count == 0: raise TimeoutError(f"thread failed to {is_alive}")
  return True
