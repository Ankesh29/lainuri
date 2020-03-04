from lainuri.config import get_config
from lainuri.logging_context import logging
log = logging.getLogger(__name__)

from lainuri.constants import Status
import lainuri.event
import lainuri.event_queue
import lainuri.rfid_reader

import traceback

#from lainuri.event import LEvent # Cannot import this even for type safety, due to circular dependency

def set_tag_alarm(event):

  try:
    lainuri.rfid_reader.set_tag_gate_alarm(event, event.on)
    lainuri.event_queue.push_event(
      lainuri.event.LESetTagAlarmComplete(
        item_barcode=event.item_barcode,
        on=event.on,
        status=Status.SUCCESS,
      )
    )
  except Exception as e:
    lainuri.event_queue.push_event(
      lainuri.event.LESetTagAlarmComplete(
        item_barcode=event.item_barcode,
        on=event.on,
        status=type(e).__name__,
        states={'exception': traceback.format_exc()}
      )
    )
