# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 11:41:51 2026

@author: Soumia
"""

import serial
import time
from enderscope import SerialDevice

class Magnetometer(SerialDevice):
    """
    eFlesh magnetometer (15 Hall sensor values :  3 axes x 5 Hall sensors) readable over serial
    """