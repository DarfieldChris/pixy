"""Module for connecting to pixy camera

   Notes:
    1 - Ony tested on Python 2.7 so far
    2 - Dependencies (PIL, SimpleCV):
           e.g. pip install PyYAML
    3 - Need to be able to find shared library ... before running python:
        LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
"""


# Standard Library Imports
from ctypes import CDLL
from ctypes import c_char_p, c_uint8, c_int8, c_uint16, c_uint32, c_int16, c_int32, c_int
from ctypes import c_void_p, pointer, Structure, byref
import logging
import time

# Third Party Imports
from PIL import Image
import SimpleCV

#Local Application/Library Specific Imports
# --- NONE ---

PIXY_TYPE_NORMAL = 0
PIXY_TYPE_COLOR_CODE = 1

PIXY_BLOCK_BUFFER_SIZE = 50

PIXY_PIXELS_WIDTH  = 320
PIXY_PIXELS_HEIGHT = 200
PIXY_PIXEL_COUNT   = PIXY_PIXELS_WIDTH*PIXY_PIXELS_HEIGHT

class PixyBlock(Structure):
    _fields_ = [ ("type", c_uint16),
                 ("signature", c_uint16),
                 ("x", c_uint16),
                 ("y", c_uint16),
                 ("width", c_uint16),
                 ("height", c_uint16),
                 ("angle", c_int16)]

PixyBlockArray = PixyBlock*PIXY_BLOCK_BUFFER_SIZE
PixyPixelArray = c_uint8*PIXY_PIXEL_COUNT

blocks = PixyBlockArray()

pixy_buf = c_void_p(0)
pixels   = PixyPixelArray()
red      = PixyPixelArray()
green    = PixyPixelArray()
blue     = PixyPixelArray()

class PixyInterpreter:
    """Class to deal with pixy camera"""

    pixylib = 'libpixyusb.so'
    rcodeInit = -1

    def __init__(self):
        """create an instance of this class
        """

        # load the libpixyusb shared library
        self._pixy = CDLL(self.pixylib)

    def __del__(self):
        self.close

    def init(self):
        self.rcodeInit = self._pixy.pixy_init()
        return self.rcodeInit

    def close(self):
        self._pixy.pixy_close()
        
    def get_blocks(self):
        """"""
        return self._pixy.pixy_get_blocks(c_uint16(PIXY_BLOCK_BUFFER_SIZE),
                                          blocks)

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

    def cam_set_auto_white_balance(self, enable):
        return self._pixy.pixy_cam_set_auto_white_balance(c_uint8(enable))

    def cam_get_auto_white_balance(self):
        return self._pixy.pixy_cam_get_auto_white_balance()

    def cam_get_white_balance_value(self):
        self._pixy.pixy_cam_get_white_balance_value.restype = c_uint32
        return self._pixy.pixy_cam_get_white_balance_value()

    def cam_set_white_balance_value(self,red,green,blue):
        return self._pixy.pixy_cam_get_white_balance_value(c_uint8(red),
                                                           c_uint8(green),
                                                           c_uint8(blue))

    def cam_set_auto_exposure_compensation(self, enable):
        return self._pixy.pixy_cam_set_auto_exposure_compensation(c_uint8(enable))

    def cam_get_auto_exposure_compensation(self):
        return self._pixy.pixy_cam_get_auto_exposure_compensation()

    def cam_set_exposure_compensation(self,gain,compensation):
        return self._pixy.pixy_cam_set_exposure_compensation(c_uint8(gain),
                                                             c_uint16(compensation))

    def cam_get_exposure_compensation(self):
        g = c_uint8(0)
        c = c_uint16(0)
        gain = pointer(g)
        compensation = pointer(c)

        rcode = self._pixy.pixy_cam_get_exposure_compensation(gain, compensation)
        return [rcode, gain.contents.value, compensation.contents.value]

    def cam_set_brightness(self,brightness):
        return self._pixy.pixy_cam_set_brightness(c_uint8(brightness))

    def cam_get_brightness(self):
        return self._pixy.pixy_cam_get_brightness()

    def rcs_get_position(self,channel):
        return self._pixy.pixy_rcs_get_position(c_uint8(channel))

    def rcs_set_position(self,channel, position):
        return self._pixy.pixy_rcs_set_position(c_uint8(channel),c_uint16(position))

    def rcs_set_frequency(self,frequency):
        return self._pixy.pixy_rcs_set_frequency(c_uint16(frequency))

    def get_firmware_version(self):
        # think this causes a small memory leak everytime it is called?
        i = c_uint16(0)
        j = c_uint16(0)
        k = c_uint16(0)

        major = pointer(i)
        minor = pointer(j)
        build = pointer(k)

        rcode = self._pixy.pixy_get_firmware_version(major,minor,build)

        return [rcode, major.contents.value, minor.contents.value, build.contents.value]
 
    def cam_setAWB(self, enable):
        response = c_int32(0) 
        self._pixy.pixy_command.argtypes = [c_char_p, c_int, c_int, c_int, c_void_p, c_int]
        rcode = self._pixy.pixy_command("cam_setAWB",  # String ID for remote procedure
                                c_int(1),              # Length (in bytes) of first arg 
                                c_int(enable),         # 1st arg ... enable 
                                c_int(0),              # seperator ... end of input values
                                byref(response),       # Pointer for return value of RPC
                                c_int(0))              # seperator ... end of output values)
        if (rcode < 0):   # error
            return rcode
        else:             # success
            return response.value

    def cam_setMode(self, mode):
        response = c_int32(0) 
        self._pixy.pixy_command.argtypes = [c_char_p, c_int, c_int, c_int, c_void_p, c_int]
        rcode = self._pixy.pixy_command("cam_setMode", # String ID for remote procedure
                                c_int(1),              # Length (in bytes) of first arg 
                                c_int(mode),           # 1st arg ... enable 
                                c_int(0),              # seperator ... end of input values
                                byref(response),       # Pointer for return value of RPC
                                c_int(0))              # seperator ... end of output values)
        if (rcode < 0):   # error
            return rcode
        else:             # success
            return response.value

    def cam_getMode(self):
        response = c_int32(0)
        self._pixy.pixy_command.argtypes = [c_char_p, c_int, c_void_p, c_int]
        rcode = self._pixy.pixy_command("cam_getMode", # String ID for remote procedure
                                c_int(0),              # seperator ... end of input values
                                byref(response),       # Pointer for return value of RPC
                                c_int(0))              # seperator ... end of output values)
        if (rcode < 0):   # error
            return rcode
        else:             # success
            return response.value

    def cam_getAWB(self):
        response = c_int32(0)
        self._pixy.pixy_command.argtypes = [c_char_p, c_int, c_void_p, c_int]
        rcode = self._pixy.pixy_command("cam_getAWB",  # String ID for remote procedure
                                c_int(0),              # seperator ... end of input values
                                byref(response),       # Pointer for return value of RPC
                                c_int(0))              # seperator ... end of output values)
        if (rcode < 0):   # error
            return rcode
        else:             # success
            return response.value

    # NOT VERY USEFUL
    def XXXcam_getFrame(self, mode=0x21, xoffset=0, yoffset=0, width=320, height=200):
        response = c_int32(0)
        resp_fourcc = c_uint32(0)
        resp_renderflags = c_int8(0)
        resp_width = c_uint16(0)
        resp_height = c_uint16(0)
        resp_numPixels = c_uint32(0)
        pixel = c_uint8(0)
        resp_ppixel = pointer(pixy_buf)

        self._pixy.pixy_command.argtypes = [c_char_p, 
                                            c_int, c_int,
                                            c_int, c_int,
                                            c_int, c_int,
                                            c_int, c_int,
                                            c_int, c_int,
                                            c_int,
                                            c_void_p, c_void_p, c_void_p,
                                            c_void_p, c_void_p, c_void_p, c_void_p,
                                            c_int]
        rcode = self._pixy.pixy_command("cam_getFrame",
                                c_int(1), c_int(mode),
                                c_int(2), c_int(xoffset),             
                                c_int(2), c_int(yoffset),             
                                c_int(2), c_int(width),             
                                c_int(2), c_int(height),             
                                c_int(0),
                                byref(response),
                                byref(resp_fourcc),
                                byref(resp_renderflags),
                                byref(resp_width),
                                byref(resp_height),
                                byref(resp_numPixels),
                                byref(pixy_buf),      
                                c_int(0))              
        if (rcode < 0):   # error
            logging.warning("pixy: cam_getFrame failed - %d - %d", rcode, response.value)
            return [rcode]
        else:             # success
            return [response.value,
                    resp_fourcc.value, resp_renderflags.value,
                    resp_width.value, resp_height.value, resp_numPixels.value,
                    pixy_buf]

    def cam_getFrame(self, mode=0x21, xoffset=0, yoffset=0, width=320, height=200):
        response = c_int32(0)
        resp_fourcc = c_uint32(0)
        resp_renderflags = c_int8(0)
        resp_width = c_uint16(0)
        resp_height = c_uint16(0)
        resp_numPixels = c_uint32(0)

        self._pixy.pixy_cam_getFrame.argtypes = [c_int,
                                            c_int, c_int,
                                            c_int, c_int,
                                            c_void_p, c_void_p, c_void_p,
                                            c_void_p, c_void_p, c_void_p, c_void_p]
        rcode = self._pixy.pixy_cam_getFrame(
                                c_int(mode),c_int(xoffset),c_int(yoffset),             
                                c_int(width),c_int(height),             
                                byref(response),
                                byref(resp_fourcc),
                                byref(resp_renderflags),
                                byref(resp_width),
                                byref(resp_height),
                                byref(resp_numPixels),
                                pixels)              
        if (rcode < 0):   # error
            logging.warning("pixy: cam_getFrame failed - %d - %d", rcode, response.value)
            return [rcode]
        else:             # success
            return [response.value,
                    resp_fourcc.value, resp_renderflags.value,
                    resp_width.value, resp_height.value, resp_numPixels.value,
                    pixels]

    def renderBA81(self, renderFlags, width, height, frameLen, frame, red, green, blue):
        self._pixy.pixy_renderBA81.argtypes = [c_uint8, c_uint16, c_uint16, c_uint32,
                                          c_void_p, c_void_p, c_void_p, c_void_p]
        rcode = self._pixy.pixy_renderBA81(
                                      c_uint8(renderFlags),
                                      c_uint16(width), c_uint16(height),
                                      c_uint32(frameLen),
                                      frame, red, green, blue)
        return rcode

    def FOURCC(self, type):
        self._pixy.pixy_FOURCC_to_string.argtypes = [c_uint32]
        self._pixy.pixy_FOURCC_to_string.restype = c_char_p

        return self._pixy.pixy_FOURCC_to_string(c_uint32(type))

if __name__ == '__main__':
    # this is the code that is run if this module is run as the main module
    # eg 'python pixy.py' OR 'python -i pixy.py'

    # set logging level and format
    logging.basicConfig(level=logging.INFO,
                        format = '%(asctime)s - %(levelname)s - %(message)s')

    #
    # Test the camera wrapper ...
    #

    # Initialize the connection
    pixy = PixyInterpreter()
    while ( pixy.init() < 0): 
        logging.warning("pixy: failed to initialize pixy connection: (%d) - %s",
                        pixy.rcodeInit, pixy.error_str(pixy.rcodeInit))
        time.sleep(5)
    logging.info("Initialized camera connection!")

    #pixy.cam_setMode(0)
    logging.info ("camera mode is %d\n", pixy.cam_getMode())

    version = pixy.get_firmware_version()
    logging.info("pixy: (return code - %d) FIRMWARE %u.%u.%u", version[0], version[1], version[2], version[3])

    #rcode = pixy.led_set_RGB(5,5,5)
    #logging.info("pixy: led_set_RGB - returned %d", rcode)

    rcode = pixy.led_get_max_current()
    logging.info("pixy: led max current: %d", rcode)
    #if (rcode == 0):
    #    rcode = 254
    #else:
    #    rcode = rcode*2
    #rc = pixy.led_set_max_current(rcode)
    #logging.info("pixy: setting max current to %d - returned %d", rcode, rc)

    rcode = pixy.led_get_max_current()
    logging.info("pixy: led max current now reads: %d", rcode)
    #rc = pixy.led_set_max_current(700)

    #pixy.cam_set_auto_white_balance(1)
    logging.info("auto_white balance set to %d\n", pixy.cam_get_auto_white_balance())

    #pixy.cam_set_white_balance_value(2,2,2)
    logging.info("white balance value %d", pixy.cam_get_white_balance_value())

    #pixy.cam_set_auto_exposure_compensation(1)
    logging.info("auto exposure compensation set to %d\n",
                 pixy.cam_get_auto_exposure_compensation())

    #pixy.cam_set_exposure_compensation(1,2)
    l = pixy.cam_get_exposure_compensation()
    logging.info("exposure compensation returned %d - gain %d - comp %d",
                 l[0], l[1], l[2])

    pixy.cam_set_brightness(90)
    logging.info("brightness set to %d\n", pixy.cam_get_brightness())

    logging.info("position %d", pixy.rcs_get_position(0))
    #pixy.rcs_set_position(0, 5)

    #pixy.rcs_set_frequency(50)

    rcode = pixy.cam_getAWB()
    logging.info("pixy: cam_getAWB: %d", rcode)
    
    #newSet = 0
    #if (rcode == 0):
    #    newSet = 1
    #rc = pixy.cam_setAWB(newSet)
    #logging.info("pixy: cam_setAWB %d - returned %d", newSet, rc)

    rcode = pixy.cam_getAWB()
    logging.info("pixy: cam_getAWB now reads: %d", rcode)
    #rc = pixy.cam_setAWB(0)

    blocks_copied = pixy.get_blocks()
    if (blocks_copied < 0):
        logging.warning("pixy: blocks_copied failed (%d) - %s", 
                         blocks_copied, pixy.get_error_str(blocks_copied))

    if (blocks_copied == 0):
        logging.info ("pixy: got %d blocks", blocks_copied);

    for i in range (0, blocks_copied-1):   
        if (blocks[i].type.value == PIXY_TYPE_NORMAL):
            logging.info("BLOCK[NORMAL]: sig:%2u w:%3u h:%3u x:%3u y:%3u]",
                blocks[i].signature.value,
                blocks[i].width.value,
                blocks[i].height.value,
                blocks[i].x.value,
                blocks[i].y.value)
        elif (blocks[i].type.value == PIXY_TYPE_COLOR_CODE):
            logging.info("BLOCK[COLOR_CODE]: sig:%2u w:%3u h:%3u x:%3u y:%3u ang:%3i]",
                blocks[i].signature.value,
                blocks[i].width.value,
                blocks[i].height.value,
                blocks[i].x.value,
                blocks[i].y.value,
                blocks[i].angle)
        else:
            logging.info("BLOCK[???]: ???")

    #pixy.close()
    #time.sleep(1)
    #while (pixy.init() >= 0):
    rcode = pixy.XXXcam_getFrame(mode=0x21, width=PIXY_PIXELS_WIDTH,
                                     height=PIXY_PIXELS_HEIGHT)
    fourcc = pixy.FOURCC(rcode[1])
    logging.info("cam_getFrame returned %d - %s", rcode[0], fourcc)

    if (fourcc == "BA81" ):

            img_width = rcode[3]-2
            img_height = rcode[4]-2
            img = Image.new("RGB", (img_width, img_height))

            pixy.renderBA81(rcode[2], rcode[3], rcode[4], rcode[5], rcode[6],
                            red, green, blue)

            for y in range (0, rcode[4]-2):
                for x in range (0, rcode[3]-2):
                    img.putpixel((x,y),
                                 (red[y*img_width + x], blue[y*img_width + x],
                                  green[y*img_width + x]))

            i = SimpleCV.Image(img)
            i.show()

            #time.sleep(2.5)

