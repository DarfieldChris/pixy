"""Module for connecting to pixy camera
"""

#Notes:
#    1 - Ony tested on Python 2.7 so far
#    2 - Dependencies:
#           pip install PyYAML
#    3 - Need to be able to find shared library ... before running python:
#           LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH


# Standard Library Imports
from ctypes import CDLL
from ctypes import c_char_p, c_uint8, c_uint16, c_uint32
from ctypes import pointer
import logging
import time

# Third Party Imports

#Local Application/Library Specific Imports
import config

class PixyInterpreter:
    """Class to deal with pixy camera"""

    pixylib = 'libpixyusb.so'
    rcodeInit = -1

    def __init__(self):
        """create an instance of this class
        """
        self._pixy = CDLL(self.pixylib)
        self.init()

    def __del__(self):
        self._pixy.pixy_close()

    def init(self):
        self.rcodeInit = self._pixy.pixy_init()
        return self.rcodeInit

    def get_blocks(self):
        """NOT IMPLEMENTED YET"""
        return -1

    def command(self, name):
        """NOT USEFUL"""
        return self._pixy.pixy_command(name)

    def error(self, rcode):
        self._pixy.pixy_error(rcode)

    def error_str(self, rcode):
        self._pixy.pixy_error_str.restype = c_char_p
        return self._pixy.pixy_error_str(rcode)

    def led_set_RGB(self, red, green, blue):
        return self._pixy.pixy_led_set_RGB(c_uint8(red),
                                           c_uint8(green),
                                           c_uint8(blue))

    def led_set_max_current(self, current):
         return self._pixy.pixy_led_set_max_current(c_uint32(current))

    def led_get_max_current(self):
         return self._pixy.pixy_led_get_max_current()

    def get_firmware_version(self):
        # think this causes a small memory leak everytime it is called?
        i = c_uint16(0)
        j = c_uint16(0)
        k = c_uint16(0)

        major = pointer(i)
        minor = pointer(j)
        build = pointer(k)

        rcode = self._pixy.pixy_get_firmware_version(major,minor,build)

        return [major.contents.value, minor.contents.value, build.contents.value]
 
if __name__ == '__main__':
    # this is the code that is run if this module is run as the main module
    # eg 'python pixy.py' OR 'python -i pixy.py'

    # set default logging level prior to parsing config info
    logging.basicConfig(level=logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

    # read config file and set logging level based on value in config file
    cfg = config.YAMLConfig()
    cfg.setLogging()

    pixy = PixyInterpreter()
    while ( pixy.rcodeInit < 0): 
        logging.warning("pixy: failed to initialize pixy connection: (%d) - %s",
                        pixy.rcodeInit, pixy.error_str(pixy.rcodeInit))
        time.sleep(5)
        pixy.init()
    logging.info("pixy: initialized connection!")

    version = pixy.get_firmware_version()
    logging.info("pixy: FIRMWARE %u.%u.%u", version[0], version[1], version[2])

    rcode = pixy.led_set_RGB(5,5,5)
    logging.info("pixy: led_set_RGB - returned %d", rcode)

    rcode = pixy.led_get_max_current()
    logging.info("pixy: led max current: %d", rcode)
    if (rcode == 0):
        rcode = 254
    else:
        rcode = rcode*2
    rc = pixy.led_set_max_current(rcode)
    logging.info("pixy: setting max current to %d - returned %d", rcode, rc)
    rcode = pixy.led_get_max_current()
    logging.info("pixy: led max current now reads: %d", rcode)
    rc = pixy.led_set_max_current(700)
   


