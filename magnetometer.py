# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 11:41:51 2026

@author: Soumia
"""

import serial
import struct
from enderscope import SerialDevice

class Magnetometer(SerialDevice):
    """
    eFlesh magnetometer (15 Hall sensor values :  3 axes x 5 Hall sensors) readable over serial
    """
    NUM_SENSORS = 5
    NUM_AXES = 3
    NUM_VALUES = NUM_SENSORS * NUM_AXES  # 15 (x, y, z without t)

    STRUCT_FORMAT = "<ffff"  # t, x, y, z float32 little-endian
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)      # 16 bytes
    FRAME_SIZE = STRUCT_SIZE * NUM_SENSORS             # 80 bytes

    def __init__(self, port, baud_rate=115200, parity=serial.PARITY_NONE,
                 stop_bits=serial.STOPBITS_ONE, byte_size=serial.EIGHTBITS):
        super().__init__(port, baud_rate, parity, stop_bits, byte_size)

    def get_reading(self):
        super().flush_serial_buffer()
        response = self.serial.read_until(b"\r\n", size=self.FRAME_SIZE + 2)
        return self._parse(response)

    def _parse(self, response: bytes):
        payload = response[:-2] if response[-2:] == b"\r\n" else response
        if len(payload) != self.FRAME_SIZE:
            print(f"Expected {self.FRAME_SIZE} bytes, got {len(payload)}")
            return None

        readings = []
        for i in range(self.NUM_SENSORS):
            chunk = payload[i * self.STRUCT_SIZE:(i + 1) * self.STRUCT_SIZE]
            t, x, y, z = struct.unpack(self.STRUCT_FORMAT, chunk)
            readings.extend([x, y, z])  # we ignore temperature t
        return readings  # 15 values