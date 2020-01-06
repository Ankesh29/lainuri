from logging_context import logging
log = logging.getLogger(__name__)

import helpers
from RL866.message import Message, Request, Response, parseMessage, parseIBlockResponseINF
import RL866.state


class IBlock(Message):
  def __init__(self, RID, INF):
    if not self.PCB:
      PCB = 0x00
      #PCB = PCB | (1<<5) # Chaining bit is set
      if RL866.state.transmission_sequence_number == 0:
        PCB = PCB & ~(1<<6)
      elif RL866.state.transmission_sequence_number == 1:
        PCB = PCB |  (1<<6)
      else:
        raise Exception(f"transmission_sequence_number '{RL866.state.transmission_sequence_number}' must be 1 or 0!")
      self.PCB = bytes([PCB])

    super().__init__(RID=RID, INF=INF)

    if isinstance(self, Request): RL866.state.increment_transmission_sequence_number()

class IBlock_ReadSystemConfigurationBlock(IBlock, Request):
  """
  The system configuration block stores information about the configuration of the
  device. When the device boots, it loads the configuration parameters and works
  according to these parameters.
  """
  CMD = b'\x01'
  def __init__(self, read_ROM=1, address=1, read_blocks=15):
    self.field1 = self.field1_CFG_block_address(address, read_ROM)
    self.field2 = self.field2_number_of_CFG_blocks_to_read(read_blocks)
    self.INF = self.CMD + self.field1 + self.field2

    super().__init__(RID=RL866.state.RID_request, INF=self.INF)

  def field1_CFG_block_address(self, address, read_ROM):
    """
    Field 1.CFG block address:
    Data type:BYTE
    bit7: 0 indicate read RAM ,1 indicates read ROM;
    bit6: set to 0, Reserved;
    bit5-0:CFG address;
    """
    field1 = bytearray([address])
    if read_ROM: field1[0] |= 1<<7
    return field1

  def field2_number_of_CFG_blocks_to_read(self, blocks: int) -> bytearray:
    return bytearray([blocks])


class IBlock_ReadSystemConfigurationBlock_Response(IBlock, Response):
  CMD = b'\x01'
  def __init__(self, resp_bytes: bytearray):
    parseMessage(self, resp_bytes)
    parseIBlockResponseINF(self)

    self.field1 = self.field1_number_of_cfg_blocks_read()
    self.field2 = self.field2_cfg_block_data_read()

    super().__init__(RID=self.RID, INF=self.INF)

  def field1_number_of_cfg_blocks_read(self):
    self.number_of_cfg_blocks_read = self.PARM[0]
    return self.PARM[0:1]
  
  def field2_cfg_block_data_read(self):
    field2 = self.PARM[1:]
    if len(field2)/14 != self.number_of_cfg_blocks_read: raise Exception(f"field2_cfg_block_data_read():> self.number_of_cfg_blocks_read '{self.number_of_cfg_blocks_read}' is different from the actual blocks read count '{len(field2)/14}' in message {self.__dict__}")
    return field2

class IBlock_TagInventory(IBlock, Request):
  CMD = b'\x31'

  stop_trigger_types = {
    "No new tag is found or timed out within Tms": 0,
    "No new tags or timeouts were detected after trying N times": 1,
    "When N tags are found or timed out": 2,
    "When the time out": 3,
  }

  def __init__(self, query_multiple_antenna=None, air_protocol_inventory_parameters=None, stop_trigger=None, new_inventory=None):
    self.INF = self.CMD

    field1 = bytearray([0x00])
    if query_multiple_antenna: field1[0] |= 1<<0
    if air_protocol_inventory_parameters: field1[0] |= 1<<1
    if stop_trigger: field1[0] |= 1<<2
    if new_inventory: field1[0] |= 1<<3
    self.INF += field1
    self.field1 = field1

    field2 = None # Antenna selection parameter
    if query_multiple_antenna:
      field2 = self.field2_query_multiple_antenna(query_multiple_antenna)
      self.INF += field2
      self.field2 = field2

    field3 = None # 
    if air_protocol_inventory_parameters:
      field3 = self.field3_air_protocol_parameter_set(air_protocol_inventory_parameters)
      self.INF += field3
      self.field3 = field3

    field4 = None
    if stop_trigger:
      field4 = self.field4_stop_trigger(stop_trigger)
      self.INF += field4
      self.field4 = field4

    super().__init__(RID=RL866.state.RID_request, INF=self.INF)

  def field2_query_multiple_antenna(self, query_multiple_antenna) -> bytearray:
    """
    Field 2.Antenna selection parameter:
      Field 2.1 Number of antenna:
      Data type:BYTE
    Field 2.2 Antenna selection bits:
      Data type:BYTE[ LEN ]
      LEN=(Number of antenna+7)/ 8
      If the corresponding bit is 1, it indicates that the corresponding
      antenna interface is selected.
    """
    field2 = bytearray()
    # TODO The manual is rather obscure about the content of the bytes
    # So skipping it's implementation specifics for now
    field2.append(1)
    field2.append(1)

    return field2

  def field3_air_protocol_parameter_set(self, parameters) -> bytearray:
    """
    Field 3.Air protocol parameter set:
      Field 3.1.Number of protocol:
        Data type:BYTE
        Indicates the number of protocols contained below
      Field 3.2 Air protocol parameter 1: Node
        Field 3.2.1. Type:
          Data type:BYTE;
          Refer to the Air Interface Protocol Type Code Table
        Field 3.2.2. Antenna interface:
          Data type:BYTE ;
          Which antenna interface the antenna is applied to 0 means it
          applies to all antenna interfaces
        Field 3.2.3 .Parameter length:
          Data type:EBV;
        Field 3.2.3 .Parameter:
          Data type:BYTE[n];
          Refer to the part “Air protocol inventory parameter”.
      Field 3.3.Air protocol parameter 2: Node
      ......
      Field 3.n Air protocol parameter N: Node
    """
    field3 = bytearray()
    field3.append(len(parameters))
    for p in parameters:
      field3.append( RL866.state.getAirProtocolCode(p) )
      field3.append( p.antenna_interface // 0 ) # Which antenna interface the antenna is applied to 0 means it applies to all antenna interfaces
      field3.append(  ) # Parameter length
      field3.append(  ) # 6.3. Air protocol inventory parameter

    return field3


  def field4_stop_trigger(self, stop_trigger) -> bytearray:
    """
    Field 4.Stop trigger parameter: Node
      Field 4.1.Type:
        Data type:BYTE
        0: No new tag is found or timed out within Tms;
        1: No new tags or timeouts were detected after trying N times;
        2 When N tags are found or timed out;
        3: When the time out;
      Field 4.2.Timeout:
        Data type:DWORD
      Field 4.3.Value:
        Data type:WORD
        When stop type = 0, this value indicates Tms;
        When Stop Type = 1, this value represents N attempts;
        When Stop Type = 2, this value indicates the discovery of N tags;
        When stop type = 3, this value is ignored;
    """
    field4 = bytearray()
    field4.append( self.stop_trigger_types[stop_trigger.type] )
    # DWORD (4 bytes)
    field4.append( stop_trigger.timeout & 0xFF000000 )
    field4.append( stop_trigger.timeout & 0x00FF0000 )
    field4.append( stop_trigger.timeout & 0x0000FF00 )
    field4.append( stop_trigger.timeout & 0x000000FF )
    # WORD (2 bytes)
    field4.append( stop_trigger.value & 0xFF00 )
    field4.append( stop_trigger.value & 0x00FF )


    return field4


class IBlock_TagInventory_Response(IBlock, Response):
  CMD = b'\x31'

  tags_buffered = -1

  def __init__(self, resp_bytes: bytearray):
      parseMessage(self, resp_bytes)
      parseIBlockResponseINF(self)

      self.field1 = self.field1_stop_byte()
      self.field2 = self.field2_total_number_of_tag_report_buffered()
      self.field3 = self.field3_the_number_of_transferring()
      
      self.fieldn = self.fieldn_tag_report()

      super().__init__(RID=self.RID, INF=self.INF)

  def field1_stop_byte(self) -> bytearray:
    """
    Data type:BYTE
    The type that triggered the inventorying stop;
     When the stop type = 0:
      the value that Tms or NAttempt or N, is triggered ,it is normal exit
      condition.
     When the stop type = 1:
      non-normal condition exit, total time-out or buffer full, indicating that
      there are more labels need to inventory, you need to issue continue inventory
      command, the bit 3 of “Field1 flag” set to 1.
    """
    return bytearray(self.PARM[0:1])

  def field2_total_number_of_tag_report_buffered(self) -> bytearray:
    """
    Data type: WORD
    The total number of tag found for this inventory
    """
    field2 = self.PARM[1:3]
    self.tags_buffered = self.PARM[1] + (self.PARM[0] <<8)
    return field2

  def field3_the_number_of_transferring(self) -> bytearray:
    """
    Data type:BYTE
    Number of reports for this transmission
    """
    field3 = self.PARM[3:4]
    self.tags_transmitted = field3[0]
    return field3

  def fieldn_tag_report(self) -> bytearray:
    """
    Field 4.1.Flag indicates fields return:
      Data type:BYTE
      b0:Antenna ID is present or not
      b1:Air protocol type ID is present or not
      b2:Tag type ID is present or not
      b3:Tag serial number is present or not
      b4:Tag memory data is present or not
      b5-6:Reserved
      b7:Embedded command is present or not
    Field 4.2 .Antenna ID:
      Data type:BYTE
      This field is only present if flag’s bit 0 is '1'
    Field 4.3.Air protocol type ID:
      Data type:BYTE
      This field is only present if bit 1 is '1'
    Field 4.4.Tag type ID:
      Data type:BYTE
      This field is only present if flag’s bit 2 is '1'
    Field 4.5.Length of serial number:
      Data type:BYTE
      This field is only present if flag’s bit 3 is '1'
    Field 4.6.Serial number:
      Data type:BYTE[ Len ]
      This field is only present if flag’s bit 3 is '1'
    Field 4.7.Number of tag memory bits:
      Data type:WORD
      Reads the number of bits in the tag memory user area
      This field is only present if flag’s bit 4 is '1'
    Field 4.8.Bit data of tag memory :
      Data type: BYTE[n]
      Reads the bit data of the tag memory user area
      This field is only present if flag’s bit 4 is '1'
    Field 4.9.Embedded commands: Node
      This field is only present if flag’s bit 7 is '1'
      Field 4.9.1 The total length of the embedded command:
        Data type:EBV
      Field 4.9.2 The length of the command result:
        Data type:EBV
      Field 4.9.3 Command code:
        Data type:WORD
      Field 4.9.4 Command status:
        Data type:BYTE
        Value 1: success,
        value 0: failure, data contains 2 error status .
      Field 4.9.5 Command return data
        Data type:BYTE[n]
    Field 5 Tag report # 2: Node
    ......
    Field n Tag report # n: Node
    """
    # Iterator is an array, because Python doesn't have references to atomic objects
    i = [4] # Start iterating the PARM after all the static fields have been processed
    self.tags = []
    for j in range(0,self.tags_transmitted):
      tag = {}
      self.tags.append(tag)

      tag['field41'] = helpers.shift_byte(self.PARM, i)
      tag['antenna_id_present']           = tag['field41'][0] & 1<<0
      tag['air_protocol_type_id_present'] = tag['field41'][0] & 1<<1
      tag['tag_type_id_present']          = tag['field41'][0] & 1<<2
      tag['tag_serial_number_present']    = tag['field41'][0] & 1<<3
      tag['tag_memory_data_present']      = tag['field41'][0] & 1<<4
      tag['embedded_command_present']     = tag['field41'][0] & 1<<7
      log.debug(f"New tag '{tag}'")

      tag['field42'] = None
      if tag['antenna_id_present']:
        tag['field42'] = helpers.shift_byte(self.PARM, i)
        tag['antenna_id'] = tag['field42'][0]
        log.debug(f"antenna id '{tag['antenna_id']}' detected")

      tag['field43'] = None
      if tag['air_protocol_type_id_present']:
        tag['field43'] = helpers.shift_byte(self.PARM, i)
        tag['air_protocol_type_id'] = tag['field43'][0]
        log.debug(f"air protocol '{RL866.state.air_protocol_type_table[tag['air_protocol_type_id']]}' detected")

      tag['field44'] = None
      if tag['tag_type_id_present']:
        tag['field44'] = helpers.shift_byte(self.PARM, i)
        tag['tag_type_id'] = tag['field44'][0]
        log.debug(f"tag type id '{tag['tag_type_id']}'")

      tag['field45'] = None
      if tag['tag_serial_number_present']:
        tag['field45'] = helpers.shift_byte(self.PARM, i)
        tag['length_of_serial_number'] = tag['field45'][0]
        log.debug(f"length of serial number '{tag['length_of_serial_number']}'")
      tag['field46'] = None
      if tag['tag_serial_number_present']:
        tag['field46'] = helpers.shift_bytes(self.PARM, i, tag['length_of_serial_number'])
        tag['serial_number'] = hex(helpers.lower_byte_fo_to_int(tag['field46']))
        log.debug(f"Received serial number '{tag['serial_number']}'")

      tag['field47'] = None
      if tag['tag_memory_data_present']:
        tag['field47'] = helpers.shift_word(self.PARM, i)
        tag['number_of_tag_memory_bits'] = tag['field47'][0]
        log.debug(f"number of tag memory bits '{tag['number_of_tag_memory_bits']}'")
      tag['field48'] = None
      if tag['tag_memory_data_present']:
        tag['field48'] = helpers.shift_bytes(self.PARM, i, tag['number_of_tag_memory_bits']/8)
        tag['tag_memory'] = hex(helpers.lower_byte_fo_to_int(tag['field48']))
        log.debug(f"Received tag memory data '{tag['tag_memory']}'")

      #TODO:: tag['field48'] Embedded commands and all the subfields
      if tag['embedded_command_present']:
        raise Exception("TODO: embedded_command_present, but no support implemented. Triggered by tag '{j}' in message {self.__dict__}")

    return self.tags

