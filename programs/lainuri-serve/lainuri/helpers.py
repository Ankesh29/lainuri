"""
Generic small utility helpers.
DO NOT import ANY lainuri.* MODULES HERE!
THIS IS imported TO lainuri.config AND THAT WOULD CAUSE GRIEVOUS CIRCULAR DEPENDENCY LOADING ISSUES
"""

from typing import Any, List
import glob
import json
import math
import os
import pathlib
import pwd
import re
import subprocess
import yaml

def _two_way_link_dict(d) -> dict:
  tmp = dict()
  for k in d:
    tmp[d[k]] = k
    tmp[k] = d[k]
  return tmp

def bytes_to_hex(bs: bytes) -> list:
  return [hex(byte) for byte in bs]

def bytes_to_hex_string(bs: bytes, prefix: str = None, suffix: str = None, hex_separator: str = " "):
  sb = []
  if prefix: sb.append(prefix)
  for byte in bs: sb.append(hex(byte))
  if suffix: sb.append(suffix)
  return hex_separator.join(sb)

def shift_byte(buffer: bytearray, iterator: list) -> bytearray:
  iterator[0] += 1 # Increment the reference to the iterator
  return buffer[ iterator[0]-1 : iterator[0] ] # Get the next byte

def shift_bytes(buffer: bytearray, iterator: list, count: int) -> bytearray:
  iterator[0] += count # Increment the reference to the iterator
  return buffer[ iterator[0]-count : iterator[0] ] # Get the next bytes

def shift_word(buffer: bytearray, iterator: list) -> bytearray:
  iterator[0] += 2
  return buffer[ iterator[0]-2 : iterator[0] ] # Get the next two bytes

def shift_dword(buffer: bytearray, iterator: list) -> bytearray:
  iterator[0] += 4
  return buffer[ iterator[0]-4 : iterator[0] ] # Get the next four bytes

def word_to_int(bs: bytes) -> int:
  if len(bs) != 2: raise Exception("word_to_int(bs):> WORD is not 2 bytes!")
  return lower_byte_fo_to_int(bs)

def dword_to_int(bs: bytes) -> int:
  if len(bs) != 4: raise Exception("dword_to_int(bs):> DWORD is not 2 bytes!")
  return lower_byte_fo_to_int(bs)

def lower_byte_fo_to_int(bs: bytes) -> int:
  """
  Multibyte fields are "inverted" when they come out of the connection.
  They are lower byte first out.

  3.Data Type Description
  Type      Description
  BYTE      8-bit data, the value range 00h-FFh
  WORD      16-bit data, the value range 0000h-FFFFh,Lower byte first out
  DWORD     32-bit data, the value range00000000h-FFFFFFFFh,Lower byte first out
  BYTE[ n ] Array type, It consists of many of BYTE types
  EBV # TODO: EBV looks like a big mess
  """
  return int.from_bytes(bs, 'little')

def int_to_byte(intgr: int) -> bytes:
  return int_to_bytes(intgr, 1)

def int_to_word(intgr: int) -> bytes:
  return int_to_bytes(intgr, 2)

def int_to_dword(intgr: int) -> bytes:
  return int_to_bytes(intgr, 4)

def int_to_bytes(intgr: int, bytes_count: int = None) -> bytes:
  if not bytes_count:
    bytes_count = math.ceil(intgr.bit_length() / 8)
  return intgr.to_bytes(bytes_count, byteorder='little')

PRIMITIVE_TYPES = (int, float, complex, str, bool, type(None))
CONTAINER_TYPES = (dict, list, tuple, range)
def null_safe_lookup(obckt, keys: List, value: Any = None) -> Any:
  """
  As Python3 doesn't seem to have a null-safe nested map/dict lookup feature, here is my own.
  Given an Object or Dict, safely lookups a nested data structure
  """
  if isinstance(keys, str): keys = keys.split('.')
  try:
    if isinstance(obckt, CONTAINER_TYPES):
      if len(keys) == 1:
        if value != None:
          obckt[keys[0]] = value
          return obckt[keys[0]]
        else:
          return obckt[keys[0]]
      return null_safe_lookup(obckt.get(keys[0], None), keys[1:], value)
    elif hasattr(obckt, '__dict__'):  # with a high probability this is a class instance or a class object
      if len(keys) == 1:
        if value != None:
          obckt[keys[0]] = value
          return getattr(obckt, keys[0])
        else:
          return getattr(obckt, keys[0])
      return null_safe_lookup(getattr(obckt, keys[0]), keys[1:], value)
    elif isinstance(obckt, PRIMITIVE_TYPES):
      return None
    else:
      raise LookupError(f"Object/Dict '{obckt}' is not a dict or object? Cannot look for keys='{keys}'")
  except IndexError:  # Accesing 0-length lists or similar raises this type of exception. We can just conclude that None is found
    return None

def find_dev_path(usb_vendor, usb_model) -> str:
  tty_lookalikes = glob.glob('/dev/ttyACM*')
  for tty_dev_path in tty_lookalikes:
    dev_info = _parse_udevadm_info(tty_dev_path)
    if dev_info['vendor_id'].upper() == usb_vendor.upper() and dev_info['model_id'].upper() == usb_model.upper():
      return tty_dev_path
  raise Exception(f"No device vendor='{usb_vendor}' model='{usb_model}' found in '{tty_lookalikes}'")

def _parse_udevadm_info(dev_path: str) -> dict:
  # pylint: disable=anomalous-backslash-in-string
  dev_info = subprocess.check_output(f"udevadm info -q all -n {dev_path}", shell=True).decode('latin1')
  parse_vendor_model = re.compile("""
    ID_VENDOR_ID=(?P<vendor_id>\w+)
    .+?
    ID_MODEL_ID=(?P<model_id>\w+)
  """, re.S | re.M | re.X)
  match = parse_vendor_model.search(dev_info)
  if match:
    return {
      'vendor_id': match.group('vendor_id'),
      'model_id':  match.group('model_id'),
    }
  raise Exception(f"Couldn't parse udevadm info '{dev_info}'")

def get_system_context():
  return {
    'cwd': pathlib.Path.cwd(),
    'pwd': pwd.getpwuid(os.getuid()),
    'lainuri_sources_path': get_lainuri_sources_Path(),
  }

def get_lainuri_sources_Path() -> pathlib.Path:
  return (pathlib.Path(__file__) / '..' / '..').resolve()

def slurp_json(path: str):
  with open(path, 'r', encoding='UTF-8') as f:
    return json.loads(f.read())

def slurp_yaml(path: str):
  with open(path, 'r', encoding='UTF-8') as f:
    return yaml.safe_load(f.read())

def append_path_to_dir(src: str, path: str, strict: bool = False):
  p = pathlib.Path(src).resolve()
  if not p.is_dir():
    p = p / '..'
  return (p / path).resolve(strict=strict)
