//
// begin license header
//
// This file is part of Pixy CMUcam5 or "Pixy" for short
//
// All Pixy source code is provided under the terms of the
// GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
// Those wishing to use Pixy source code, software and/or
// technologies under different licensing terms should contact us at
// cmucam@cs.cmu.edu. Such licensing terms are available for
// all portions of the Pixy codebase presented here.
//
// end license header
//

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include "pixy.h"

#define BLOCK_BUFFER_SIZE    25
#define FOURCC(a, b, c, d)  (((uint32_t)a<<0)|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24))

// Pixy Block buffer // 
struct Block blocks[BLOCK_BUFFER_SIZE];


int parseFOURCC(uint32_t type) {
    int res;
    // choose fourcc for representing formats fourcc.org
    if (type==FOURCC('B','A','8','1'))
        res = 1;
    else if (type==FOURCC('C','C','Q','1'))
        res = 2;
    else if (type==FOURCC('C', 'C', 'B', '1'))
        res = 3;
    else if (type==FOURCC('C', 'M', 'V', '1'))
        res = 4;
    else // format not recognized
        res = 0;
}

int getFrame(int32_t *presponse, 
    uint32_t *pfourcc,
    int8_t *prenderflags,
    uint16_t *pwidth, uint16_t *pheight,
    uint32_t *pnumPixels,
    uint8_t **pframe)
{

    int ret;

    *presponse = 0;
    ret=0;
    //printf("Before call: %p\n", (void *)frame);
    ret = pixy_command("cam_getFrame",  // String id for remote procedure
				 0x01,0x21,      // mode
                                 0x02,0,         // xoffset
                                 0x02,0,         // yoffset
                                 0x02,320,       // width
                                 0x02,200,       // height
                                 0,              // separator
                                 presponse,      // pointer to mem address for return value
				 pfourcc,
				 prenderflags,
				 pwidth,
				 pheight,
				 pnumPixels,
                                 pframe,     // pointer to mem address for returned frame
                                 0);
    if (ret < 0) {
	return ret;
    } else {
        // convert type to something a little more readable
        *pfourcc = parseFOURCC(*pfourcc);
        return *presponse;
    }
}



void handle_SIGINT(int unused)
{
  // On CTRL+C - abort! //

  printf("\nBye!\n");
  exit(0);
}


int main(int argc, char * argv[])
{
  int     return_value, res;

  int      index;
  int      blocks_copied;
  int      pixy_init_status;

  // Catch CTRL+C (SIGINT) signals //
  signal(SIGINT, handle_SIGINT);

  printf("Hello Pixy:\n libpixyusb Version: %s\n", __LIBPIXY_VERSION__);

  // Connect to Pixy //
  pixy_init_status = pixy_init();
  printf("Hello Pixy: initialized Pixy - %d\n", pixy_init_status);

  // Was there an error initializing pixy? //
  if(!pixy_init_status == 0)
  {
    // Error initializing Pixy //
    printf("pixy_init(): ");
    pixy_error(pixy_init_status);
    printf("    If on RPi did you 'su' before running?\n");

    return pixy_init_status;
  }

  // Request Pixy firmware version //
  {
    uint16_t major;
    uint16_t minor;
    uint16_t build;
    int      return_value;

    return_value = pixy_get_firmware_version(&major, &minor, &build);

    if (return_value) {
      // Error //
      printf("Failed to retrieve Pixy firmware version. %d", return_value);
      pixy_error(return_value);

      return return_value;
    } else {
      // Success //
      printf(" Pixy Firmware Version: %d.%d.%d\n", major, minor, build);
    }
  }

  
  // Pixy Command Examples //
  {
    unsigned char pixels[907200];
    uint8_t *frame = (uint8_t *)&pixels[0];
    //uint8_t *frame;
    int32_t response;
    uint32_t fourcc;
    int8_t renderflags;
    uint16_t width, height;
    uint32_t numPixels;

    response = 0;
    return_value=0;
    //printf("Before call: %p\n", (void *)frame);
    return_value = pixy_command("cam_getFrame",  // String id for remote procedure
				 0x01,0x21,      // mode
                                 0x02,0,         // xoffset
                                 0x02,0,         // yoffset
                                 0x02,320,       // width
                                 0x02,200,       // height
                                 0,              // separator
                                 &response,      // pointer to mem address for return value
				 &fourcc,
				 &renderflags,
				 &width,
				 &height,
				 &numPixels,
                                 &frame,     // pointer to mem address for returned frame
                                 0);
    printf("Returned -  [%d] - %d - %d - %d - %d - %d %p\n", 
             return_value, response ,
	     parseFOURCC(fourcc), int(width), (int)height, (int)numPixels, (void *)frame);
    fprintf(stderr,"getFrame returned: %d - %d\n", return_value, response);
    pixy_error(return_value);
    //exit(return_value);

    return_value = getFrame(&response, &fourcc, &renderflags, &width, &height, &numPixels, &frame);
    printf("Returned -  [%d] - %d - %d - %d - %d - %d %p\n", 
             return_value, response ,
	     int(fourcc), int(width), (int)height, (int)numPixels, (void *)frame);
    fprintf(stderr,"getFrame returned: %d - %d\n", return_value, response);
    pixy_error(return_value);

    // Execute remote procedure call "cam_setAWB" with one output (host->pixy) parameter (Value = 1)
    //
    //   Parameters:                 Notes:
    //
    //   pixy_command("cam_setAWB",  String identifier for remote procedure
    //                        0x01,  Length (in bytes) of first output parameter
    //                           1,  Value of first output parameter
    //                           0,  Parameter list seperator token (See value of: END_OUT_ARGS)
    //                   &response,  Pointer to memory address for return value from remote procedure call
    //                           0); Parameter list seperator token (See value of: END_IN_ARGS)
    //

    // Enable auto white balance //
    return_value = pixy_command("cam_setAWB", 0x01, 1, 0, &response, 0);

    // Execute remote procedure call "cam_getAWB" with no output (host->pixy) parameters
    //
    //   Parameters:                 Notes:
    //
    //   pixy_command("cam_setAWB",  String identifier for remote procedure
    //                           0,  Parameter list seperator token (See value of: END_OUT_ARGS)
    //                   &response,  Pointer to memory address for return value from remote procedure call
    //                           0); Parameter list seperator token (See value of: END_IN_ARGS)
    //

    // Get auto white balance //
    return_value = pixy_command("cam_getAWB", 0, &response, 0);

    // Set auto white balance back to disabled //
    pixy_command("cam_setAWB", 0x01, 0, 0, &response, 0);

  }

  printf("Detecting blocks...\n");

  //for(;;)
  {
    printf(".");
    fflush(stdout);

    // Get blocks from Pixy //
    blocks_copied = pixy_get_blocks(BLOCK_BUFFER_SIZE, &blocks[0]);

    //res = cam_getFrame();

    if(blocks_copied < 0) {
      // Error: pixy_get_blocks //
      printf("\npixy_get_blocks(): ");
      pixy_error(blocks_copied);
      usleep(250000);
    }

    // Display received blocks //
    for(index = 0; index != blocks_copied; ++index) {

      switch (blocks[index].type) {
        case TYPE_NORMAL:
          printf("\n[sig:%2u w:%3u h:%3u x:%3u y:%3u]",
                 blocks[index].signature,
                 blocks[index].width,
                 blocks[index].height,
                 blocks[index].x,
                 blocks[index].y);
        break;

        case TYPE_COLOR_CODE:
          printf("\n[sig:%2u w:%3u h:%3u x:%3u y:%3u ang:%3i]",
                 blocks[index].signature,
                 blocks[index].width,
                 blocks[index].height,
                 blocks[index].x,
                 blocks[index].y,
                 blocks[index].angle);
        break;
      }
      printf("\n"); 
    }

    // Sleep for 1/10 sec //
    usleep(100000);
  }
}
