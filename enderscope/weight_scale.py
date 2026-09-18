"""The serial weight scale"""

import serial
import time
from .serial_device import SerialDevice

class WeightScale(SerialDevice):
    """
    A weight scale able to be read over serial
    """

    def __init__(self, port, baud_rate=9600, parity=serial.PARITY_NONE,
                 stop_bits=serial.STOPBITS_ONE, byte_size=serial.EIGHTBITS):
        super().__init__(port, baud_rate, parity, stop_bits, byte_size)
        
    def write(self, code, check_response=True):
        super().flush_serial_buffer()
        super().write_code(code)
        response = None
        if check_response:
            response = self.serial.read_until(b"\r\n",size=256)
        return response

    def get_stable_reading(self):
        response = self.write(f"s")
        return self._parse(response)

    def get_instant_reading(self):
        done = self.write(f"w")
        return self._parse(done)

    def perform_tare(self, max_delay=5):
        self.write(f"t", check_response=False)
        timeout = time.time() + max_delay
        while True: 
            if time.time() > timeout :
                print("Tare did not work before timeout")
                break
            if self.get_stable_reading() == 0:
                break

    def _parse(self, response: bytes):
        if len(response) > 0 :
            try:
                sign = 1
                decoded = response.decode("ascii")
                if decoded.startswith("-"):
                    decoded = decoded[1:]
                    sign = -1
                decoded = sign * float(decoded.split()[0])
                return decoded
            except (UnicodeDecodeError, ValueError, IndexError):
                print("Error while decoding scale answer:", response)
                return None
        else:
            print("Empty answer from scale")
            return None