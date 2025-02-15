import context

import lainuri.event

def test_message_parsing():
  event = lainuri.event.parseEventFromWebsocketMessage(
    """{
      "event": "register-client",
      "message": {},
      "event_id": "register-client-2"
    }""",
    'client'
  )
  assert event
  assert event.event == 'register-client'

  event = lainuri.event.parseEventFromWebsocketMessage(
    """{
      "event": "ringtone-play-complete",
      "message": {
        "ringtone_type": "check-in",
        "ringtone": ""
      },
      "event_id": "ringtone-play-complete-3"
    }""",
    'client'
  )
  assert event
  assert event.event == 'ringtone-play-complete'
  assert event.ringtone_type == 'check-in'
