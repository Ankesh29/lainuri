'use strict';

let event_id = 0;
function get_event_id(event_name) {
  return event_name + '-' + event_id++;
}

const Status = Object.freeze({
  "SUCCESS":"SUCCESS",
  "ERROR":"ERROR",
  "PENDING":"PENDING",
  "NOT_SET":"NOT_SET",
})

class LEvent {

  event
  message;
  raw_data;
  sender;
  recipient;
  default_dispatch = undefined;
  event_id;

  constructor(event_id = undefined) {
    let constr = this.constructor; // As the this.event is static, it doesn't mix transparently with other class instance attributes
    this.event = constr.event;
    if (! this.event) { throw new Error(`Message '${constr}' is missing static attribute event!`) }

    this.event_id = event_id;
    if (! this.event_id) this.event_id = get_event_id(this.event)
  }
  construct(sender = undefined, recipient = undefined) {
    this.sender = sender;
    this.recipient = recipient;
  }
  validate_params() {
    this.constructor.serializable_attributes.forEach((attribute_name) => {
      if (!(this[attribute_name]) && (this[attribute_name] === undefined || this[attribute_name] === null)) {
        this.throw_missing_attribute(attribute_name)
      }
    });
  }

  serialize_for_ws() {
    let message = this.constructor.serializable_attributes.reduce(
      (attributes, attribute_name) => {
        attributes[attribute_name] = this[attribute_name];
        return attributes;
      }, {}
    )
    return JSON.stringify({
      'event': this.event,
      'message': message,
      'event_id': this.event_id,
    });
  }

  throw_missing_attribute(attribute_name) {
    let class_name = this.constructor.name;
    throw new Error(`${class_name}():> Missing attribute '${attribute_name}'`);
  }
}

class LEAdminModeEnter extends LEvent {
  static event = 'admin-mode-enter';
  default_dispatch = 'client';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}

class LEAdminModeLeave extends LEvent {
  static event = 'admin-mode-leave';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}

class LECheckOut extends LEvent {
  static event = 'check-out';

  static serializable_attributes = ['item_barcode', 'user_barcode', 'tag_type'];
  item_barcode;
  user_barcode;
  tag_type;

  constructor(item_barcode, user_barcode, tag_type = 'rfid', sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode;
    this.user_barcode = user_barcode;
    this.tag_type = tag_type;
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LECheckOutComplete extends LEvent {
  static event = 'check-out-complete';

  static serializable_attributes = ['item_barcode', 'user_barcode', 'tag_type', 'status', 'states'];
  item_barcode;
  user_barcode;
  tag_type;
  states;
  status = Status.NOT_SET;

  constructor(item_barcode, user_barcode, tag_type = 'rfid', status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode
    this.user_barcode = user_barcode
    this.tag_type = tag_type
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LECheckIn extends LEvent {
  static event = 'check-in';

  static serializable_attributes = ['item_barcode', 'tag_type'];
  item_barcode;
  tag_type;

  constructor(item_barcode, tag_type = 'rfid', sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode;
    this.tag_type = tag_type;
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LECheckInComplete extends LEvent {
  static event = 'check-in-complete';

  static serializable_attributes = ['item_barcode', 'sort_to', 'tag_type', 'status', 'states'];
  item_barcode;
  sort_to;
  tag_type;
  states;
  status = Status.NOT_SET;

  constructor(item_barcode, sort_to, tag_type = 'rfid', status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_barcode = item_barcode
    this.sort_to = sort_to
    this.tag_type = tag_type;
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LELocaleSet extends LEvent {
  static event = 'locale-set'
  default_dispatch = 'server'

  static serializable_attributes = ['locale_code']
  locale_code;

  constructor(locale_code, sender, recipient, event_id = undefined) {
    super(event_id);
    this.locale_code = locale_code
    this.construct(sender, recipient);
    this.validate_params()
  }
}

class LETransactionHistoryRequest extends LEvent {
  static event = 'transaction-history-request'
  default_dispatch = 'server'

  static serializable_attributes = ['start_time','end_time']
  start_time;
  end_time;

  constructor(start_time, end_time, sender, recipient, event_id = undefined) {
    super(event_id);
    this.start_time = start_time
    this.end_time = end_time
    this.construct(sender, recipient);
    this.validate_params()
  }
}

class LETransactionHistoryResponse extends LEvent {
  static event = 'transaction-history-response'
  default_dispatch = 'client'

  static serializable_attributes = ['transactions', 'status', 'states']
  transactions;
  states;
  status;

  constructor(transactions, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.transactions = transactions
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}

class LESetTagAlarm extends LEvent {
  static event = 'set-tag-alarm';

  static serializable_attributes = ['item_barcode', 'on'];
  item_barcode;
  on;

  constructor(item_barcode, on, sender, recipient, event_id) {
    super(event_id)
    this.item_barcode = item_barcode
    this.on = on
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LESetTagAlarmComplete extends LEvent {
  static event = 'set-tag-alarm-complete'

  static serializable_attributes = ['item_barcode', 'on', 'status', 'states']
  item_barcode;
  on;
  states;
  status = Status.NOT_SET;

  constructor(item_barcode, on, status, states, sender, recipient, event_id) {
    super(event_id)
    this.item_barcode = item_barcode
    this.on = on
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params();
  }
}

class LEBarcodeRead extends LEvent {
  static event = 'barcode-read';

  static serializable_attributes = ['barcode', 'tag'];
  barcode;
  tag;

  constructor(barcode, tag, sender, recipient, event_id = undefined) {
    super(event_id);
    this.barcode = barcode;
    this.tag = tag;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LERingtonePlay extends LEvent {
  static event = 'ringtone-play';
  default_dispatch = 'server';

  static serializable_attributes = ['ringtone_type', 'ringtone'];
  ringtone_type;
  ringtone;

  constructor(ringtone_type = undefined, ringtone = undefined, sender, recipient, event_id = undefined) {
    super(event_id);
    this.ringtone_type = ringtone_type;
    this.ringtone = ringtone;
    this.construct(sender, recipient);
    if (!(this.ringtone_type) && !(this.ringtone)) { this.throw_missing_attribute("ringtone_type' or 'ringtone'") }
  }
}
class LERingtonePlayComplete extends LEvent {
  static event = 'ringtone-play-complete';

  static serializable_attributes = ['status', 'ringtone_type', 'ringtone', 'states'];
  ringtone_type;
  ringtone;
  states;
  status = Status.NOT_SET;

  constructor(status, ringtone_type = undefined, ringtone = undefined, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.ringtone_type = ringtone_type;
    this.ringtone = ringtone;
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    if (!(this.ringtone_type) && !(this.ringtone)) { this.throw_missing_attribute("ringtone_type' or 'ringtone'") }
  }
}
class LEConfigGetpublic extends LEvent {
  static event = 'config-getpublic';
  default_dispatch = 'server';

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}
class LEConfigGetpublic_Response extends LEvent {
  static event = 'config-getpublic-response';

  static serializable_attributes = ['config'];
  config;

  constructor(config, sender, recipient, event_id = undefined) {
    super(event_id);
    this.config = config;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LEConfigWrite extends LEvent {
  static event = 'config-write';
  default_dispatch = 'server';

  static serializable_attributes = ['variable', 'new_value'];
  variable;
  new_value;

  constructor(variable, new_value, sender, recipient, event_id = undefined) {
    super(event_id);
    this.variable = variable;
    this.new_value = new_value;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEItemBibFullDataRequest extends LEvent {
  static event = 'itembib-fulldata-request'
  default_dispatch = 'server'

  static serializable_attributes = ['barcodes']

  barcodes;

  constructor(barcodes, sender, recipient, event_id = undefined) {
    super(event_id);
    this.barcodes = barcodes
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEItemBibFullDataResponse extends LEvent {
  static event = 'itembib-fulldata-response'
  default_dispatch = 'client'

  static serializable_attributes = ['item_bibs']

  item_bibs;

  constructor(item_bibs, sender, recipient, event_id = undefined) {
    super(event_id);
    this.item_bibs = item_bibs
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LELogSend extends LEvent {
  static event = 'log-send'
  default_dispatch = 'server'

  static serializable_attributes = ['messages']
  messages;

  constructor(messages, sender, recipient, event_id = undefined) {
    super(event_id);
    this.messages = messages;
    this.construct(sender, recipient);
    this.validate_params();
  }
}
class LELogReceived extends LEvent {
  static event = 'log-received'

  static serializable_attributes = ['status', 'states']
  states;
  status = Status.NOT_SET

  constructor(status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintRequest extends LEvent {
  static event = 'print-request'
  default_dispatch = 'server'

  static serializable_attributes = ['receipt_type', 'items', 'user_barcode']
  receipt_type;
  items;
  user_barcode;

  constructor(receipt_type, items, user_barcode, sender, recipient, event_id = undefined) {
    super(event_id);
    this.receipt_type = receipt_type;
    this.items = items
    this.user_barcode = user_barcode
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintResponse extends LEvent {
  static event = 'print-response'

  static serializable_attributes = ['receipt_type', 'items', 'user_barcode', 'printable_sheet', 'status', 'states']
  receipt_type;
  items;
  user_barcode;
  printable_sheet;
  states;
  status = Status.NOT_SET

  constructor(receipt_type, items, user_barcode, printable_sheet, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.receipt_type = receipt_type
    this.items = items
    this.user_barcode = user_barcode
    this.printable_sheet = printable_sheet
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintTemplateList extends LEvent {
  static event = 'print-template-list'
  default_dispatch = 'server'

  static serializable_attributes = []

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintTemplateListResponse extends LEvent {
  static event = 'print-template-list-response'

  static serializable_attributes = ['templates', 'status', 'states']
  templates;
  states;
  status;

  constructor(templates, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.templates = templates
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintTemplateSave extends LEvent {
  static event = 'print-template-save'
  default_dispatch = 'server'

  static serializable_attributes = ['id', 'type', 'locale_code', 'template']
  id;
  type;
  locale_code;
  template;

  constructor(id, type, locale_code, template, sender, recipient, event_id = undefined) {
    super(event_id);
    this.id = id
    this.type = type
    this.locale_code = locale_code
    this.template = template
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintTemplateSaveResponse extends LEvent {
  static event = 'print-template-save-response'

  static serializable_attributes = ['id', 'type', 'locale_code', 'status', 'states']
  id;
  type;
  locale_code;
  status;
  states;

  constructor(id, type, locale_code, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.id = id
    this.type = type
    this.locale_code = locale_code
    this.status = status
    this.states = states
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintTestRequest extends LEvent {
  static event = 'print-test-request'
  default_dispatch = 'server'

  static serializable_attributes = ['template', 'data', 'css', 'real_print']
  template;
  data;
  css;
  real_print;

  constructor(template, data, css, real_print, sender, recipient, event_id = undefined) {
    super(event_id);
    this.template = template
    this.data = data
    this.css = css
    this.real_print = real_print
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEPrintTestResponse extends LEvent {
  static event = 'print-test-response'

  static serializable_attributes = ['image', 'status', 'states']
  image;
  states;
  status;

  constructor(image, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.image = image
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsNew extends LEvent {
  static event = 'rfid-tags-new';

  static serializable_attributes = ['tags_new','tags_present', 'status', 'states'];
  tags_new;
  tags_present;
  status;
  states;

  constructor(tags_new, tags_present, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.tags_new = tags_new;
    this.tags_present = tags_present;
    this.status = status;
    this.states = states;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsLost extends LEvent {
  static event = 'rfid-tags-lost';

  static serializable_attributes = ['tags_lost','tags_present'];
  tags_lost;
  tags_present;

  constructor(tags_lost, tags_present, sender, recipient, event_id = undefined) {
    super(event_id);
    this.tags_lost = tags_lost;
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LERFIDTagsPresentRequest extends LEvent {
  static event = 'rfid-tags-present-request';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}
class LERFIDTagsPresent extends LEvent {
  static event = 'rfid-tags-present';

  static serializable_attributes = ['tags_present'];
  tags_present;

  constructor(tags_present, sender, recipient, event_id = undefined) {
    super(event_id);
    this.tags_present = tags_present;
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEServerConnected extends LEvent {
  static event = 'server-connected';

  constructor(event_id = undefined) {
    super(event_id);
  }
}
class LEServerDisconnected extends LEvent {
  static event = 'server-disconnected';

  constructor(event_id = undefined) {
    super(event_id);
  }
}
class LEServerStatusRequest extends LEvent {
  static event = 'server-status-request';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}

class LEServerStatusResponse extends LEvent {
  static event = 'server-status-response';

  static serializable_attributes = ['statuses'];
  statuses;

  constructor(statuses, sender, recipient, event_id = undefined) {
    super(event_id);
    this.statuses = statuses
    this.construct(sender, recipient);
    this.validate_params()
  }
}

class LEUserLoggingIn extends LEvent {
  static event = 'user-logging-in';
  default_dispatch = 'server';

  static serializable_attributes = ['username, password'];
  username;
  password;

  constructor(username = '', password = '', sender, recipient, event_id = undefined) {
    super(event_id);
    this.username = username;
    this.password = password;
    this.construct(sender, recipient);
    //this.validate_params()
  }
}
class LEUserLoginComplete extends LEvent {
  static event = 'user-login-complete';

  static serializable_attributes = ['firstname', 'surname', 'user_barcode', 'status', 'states'];
  firstname;
  surname;
  user_barcode;
  password;
  states;
  status = Status.NOT_SET;

  constructor(firstname, surname, user_barcode, status, states, sender, recipient, event_id = undefined) {
    super(event_id);
    this.firstname = firstname;
    this.surname = surname;
    this.user_barcode = user_barcode;
    this.states = states
    this.status = status
    this.construct(sender, recipient);
    this.validate_params()
  }
}
class LEUserLoginAbort extends LEvent {
  static event = 'user-login-abort';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(sender, recipient, event_id = undefined) {
    super(event_id);
    this.construct(sender, recipient);
  }
}
class LEException extends LEvent {
  static event = 'exception';

  static serializable_attributes = ['etype','description','trace'];
  etype;
  description;
  trace;

  constructor(etype, description, trace, sender, recipient, event_id = undefined) {
    super(event_id);
    if (etype instanceof Error) {
      this.etype = etype.getClass().getCanonicalName();
      this.description = etype+"";
      this.trace = etype.stack
    }
    else {
      this.etype = etype;
      this.description = description;
      this.trace = trace;
    }
    this.construct(sender, recipient);
    this.validate_params()
  }
}

/**
 * Trigger the server to send mocked RFID tag reads and barcode reads
 */
class LETestMockDevices extends LEvent {
  static event = 'test-mock-devices';
  default_dispatch = 'server';

  static serializable_attributes = [];

  constructor(event_id = undefined) {
    super(event_id);
  }
}

export {
  Status, LEvent, LEException, LEAdminModeLeave, LEAdminModeEnter, LEBarcodeRead, LECheckIn, LECheckInComplete, LEItemBibFullDataRequest, LEItemBibFullDataResponse, LELogSend, LELogReceived, LELocaleSet, LETransactionHistoryRequest, LETransactionHistoryResponse, LESetTagAlarm, LESetTagAlarmComplete, LECheckOut, LECheckOutComplete, LEConfigWrite, LEConfigGetpublic, LEConfigGetpublic_Response, LEPrintRequest, LEPrintResponse, LEPrintTemplateList, LEPrintTemplateListResponse, LEPrintTemplateSave, LEPrintTemplateSaveResponse, LEPrintTestRequest, LEPrintTestResponse, LERFIDTagsLost, LERFIDTagsNew, LERFIDTagsPresentRequest, LERFIDTagsPresent, LERingtonePlay, LERingtonePlayComplete, LEServerConnected, LEServerDisconnected, LEServerStatusRequest, LEServerStatusResponse, LETestMockDevices, LEUserLoginComplete, LEUserLoggingIn, LEUserLoginAbort
}
