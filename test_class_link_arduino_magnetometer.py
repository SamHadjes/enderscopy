# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 15:18:01 2026

@author: Soumia
"""

from magnetometer import Magnetometer
import time

mag = Magnetometer(port="COM3", baud_rate=115200)  # port à adapter

try:
    while True:
        values = mag.get_reading()
        print(values)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass