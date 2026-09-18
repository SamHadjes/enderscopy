# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 11:41:51 2026

@author: Soumia
"""
import serial
import struct
import csv
import time
import threading
import numpy as np
from enderscope import SerialDevice

class Magnetometer(SerialDevice):
    """
    eFlesh magnetometer (15 Hall sensor values :  3 axes x 5 Hall sensors) readable over serial
    """

    NUM_SENSORS = 5
    NUM_AXES = 3
    NUM_VALUES = NUM_SENSORS * NUM_AXES  # 15 (x, y, z par capteur, sans t)

    STRUCT_FORMAT = "<ffff"  # t, x, y, z en float32 little-endian
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)      # 16 octets
    FRAME_SIZE = STRUCT_SIZE * NUM_SENSORS             # 80 octets

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
            readings.extend([x, y, z])  # on garde x,y,z, on ignore t
        return readings  # 15 valeurs

    def acquire_baseline(self, num_samples=5):
        samples = []
        while len(samples) < num_samples:
            reading = self.get_reading()
            if reading is not None:
                samples.append(reading)
        return np.mean(samples, axis=0)


class MagnetometerLogger(threading.Thread):
    """
    Lit le magnétomètre en continu dans un thread séparé de l'aquisition en force/déplacement
    """

    def __init__(self, mag, baseline,
                 sensor_path='sensor.csv',
                 corrected_path='sensor_post_baselines.csv'):
        super().__init__(daemon=True)
        self.mag = mag
        self.baseline = baseline
        self.sensor_path = sensor_path
        self.corrected_path = corrected_path
        self._running = threading.Event()

    def run(self):
        self._running.set()
        with open(self.sensor_path, 'w', newline='') as f_sensor, \
             open(self.corrected_path, 'w', newline='') as f_corrected:

            writer_sensor = csv.writer(f_sensor)
            writer_corrected = csv.writer(f_corrected)

            while self._running.is_set():
                values = self.mag.get_reading()
                if values is not None:
                    timestamp = time.time()
                    corrected = np.array(values) - self.baseline
                    writer_sensor.writerow([timestamp, *values])
                    writer_corrected.writerow([timestamp, *corrected])

    def stop(self):
        self._running.clear()