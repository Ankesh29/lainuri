#!/usr/bin/python3

import serial
import time

from logging_context import logging
from RL866.sblock import SBlock_RESYNC, SBlock_RESYNC_Response
from RL866.iblock import IBlock_ReadSystemConfigurationBlock, IBlock_ReadSystemConfigurationBlock_Response, IBlock_TagInventory, IBlock_TagInventory_Response, IBlock_TagConnect, IBlock_TagConnect_Response, IBlock_TagDisconnect, IBlock_TagDisconnect_Response
import RL866.state

log = logging.getLogger(__name__)

def bic(bin: str):
  return chr(int(str(bin),2))

def hic(hex: str):
  return chr(int(str(hex),16))

def iic(i: int):
  return chr(i)

def bi(bin: str):
  return chr(int(str(bin),2))

def hi(hex: str):
  return chr(int(str(hex),16))

def ii(i: int):
  return chr(i)


def write(ser, msg):
  log.info(f"WRITE--> {type(msg)}")
  data = msg.pack()
  for b in data: print(hex(b), ' ', end='')
  print()
  rv = ser.write(data)
  log.info(rv)
  log.info(f"-->WRITE {type(msg)}")
  return rv

timeout = 5
def read(ser, msg_class: type):
  log.info(f"READ WAITING--> {msg_class}")
  slept = 0
  while(ser.in_waiting == 0):
    time.sleep(0.1)
    slept += 0.1
    if slept > timeout:
      raise Exception("read timeout")

  log.info(f"READ--> {msg_class}")
  #rv = ser.read(255)
  rv = ser.readline()
  for b in rv: print(hex(b), ' ', end='')
  # Read again after a small break, to see if there is something more to read.
  time.sleep(0.1)
  rv2 = ser.readline()
  for b in rv2: print(hex(b), ' ', end='')
  print()
  msg = msg_class(rv+rv2)
  log.info(f"-->READ {msg}")
  return msg

ser = serial.Serial()
ser.baudrate = 38400
ser.parity = serial.PARITY_EVEN
ser.port = '/dev/ttyUSB0'
ser.timeout = 0
ser.open()

log.info("\n-------serial-------")
log.info(ser.__dict__)

log.info("\n-------RESYNC-------")
msg = SBlock_RESYNC()
write(ser, msg)
msg = read(ser, SBlock_RESYNC_Response)

log.info("\n-------IBlock_ReadSystemConfigurationBlock-------")
msg = IBlock_ReadSystemConfigurationBlock(read_ROM=0, read_blocks=1)
write(ser, msg)
msg = read(ser, IBlock_ReadSystemConfigurationBlock_Response)

log.info("\n-------IBlock_ReadSystemConfigurationBlock-------")
msg = IBlock_ReadSystemConfigurationBlock()
write(ser, msg)
msg = read(ser, IBlock_ReadSystemConfigurationBlock_Response)

log.info("\n-------IBlock_TagInventory-------")
msg = IBlock_TagInventory()
write(ser, msg)
msg = read(ser, IBlock_TagInventory_Response)
tag = msg.tags[0]

log.info("\n-------IBlock_TagConnect-------")
msg = IBlock_TagConnect(tag)
write(ser, msg)
msg = read(ser, IBlock_TagConnect_Response)
msg.bind_tag(tag)

log.info("\n-------IBlock_TagDisconnect-------")
msg = IBlock_TagDisconnect(tag)
write(ser, msg)
msg = read(ser, IBlock_TagDisconnect_Response)
msg.disconnect_tag(tag)
