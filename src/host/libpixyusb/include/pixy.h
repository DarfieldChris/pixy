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

#ifndef __PIXY_H__
#define __PIXY_H__

#include <stdint.h>
#include <unistd.h>
#include <pixydefs.h>

// Pixy C API //

#ifdef __cplusplus
extern "C"
{
#endif

  #define TYPE_NORMAL                           0
  #define TYPE_COLOR_CODE                       1

  #define CAMERA_MODE_25FPS_1280X800            0
  #define CAMERA_MODE_50FPS_640X400             1

  struct Block
  {
    uint16_t type;
    uint16_t signature;
    uint16_t x;
    uint16_t y;
    uint16_t width;
    uint16_t height;
    int16_t  angle;
  };

  /**
    @brief Creates a connection with Pixy and listens for Pixy messages.
    @return   0   Success
    @return  -1   Error
  */
  int pixy_init();

  /**
    @brief      Copies up to 'max_blocks' number of Blocks to the address pointed
                to by 'blocks'.
    @param[in]  max_blocks Maximum number of Blocks to copy to the address pointed to
                           by 'blocks'.
    @param[out] blocks     Address of an array in which to copy the blocks to.
                           The array must be large enough to write 'max_blocks' number
                           of Blocks to.
    @return     Number of blocks copied.
  */
  uint16_t pixy_get_blocks(uint16_t max_blocks, struct Block * blocks);

  /**
    @brief      Send a command to Pixy.
    @param[in]  name  Chirp remote procedure call identifier string.
    @return     -1    Error

  */
  int pixy_command(const char *name, ...);

  /**
    @brief Terminates connection with Pixy.
  */
  void pixy_close();

  /**
    @brief     Set Pixy camera mode
    @param[in] mode  Camera mode.
    @return     0    Success
    @return    -1    Error
  */
  int      pixy_set_camera_mode(int mode);

  /**
    @brief     Get Pixy camera mode.
    @return     0    Camera Mode 0: 25 FPS, 1280x800
    @return     1    Camera Mode 1: 50 FPS, 640x400
    @return    -1    Error
  */
  int      pixy_get_camera_mode();

  /**
    @brief    Enable or disable auto white balance.
    @param    value  true:  Enable white balance.
                     false: Disable white balance.
    @return     0    Success
    @return    -1    Error

  */
  int      pixy_set_auto_white_balance(int value);

  /**
    @brief    Get auto white balance setting.
    @return   true    Auto white balance is enabled.
    @return   false   Auto white balance is disabled.
  */
  int      pixy_get_auto_white_balance();

  /**
    @brief    Set camera white balance.
    @param    white_balance
    @return     0     Success
    @return    -1     Error
  */
  int      pixy_set_white_balance(uint32_t white_balance);

  /**
    @brief   Get camera white balance();

  */
  uint32_t pixy_get_white_balance();
  int      pixy_set_auto_exposure_compensation(int enabled);
  int      pixy_get_auto_exposure_compensation() ;
  int      pixy_set_exposure_compensation(uint32_t compensation);
  int      pixy_set_brightness(uint8_t brightness);
  uint8_t  pixy_get_brightness();
  int      pixy_set_light_mode(uint8_t mode);
  int      pixy_get_light_mode();

  // Add:
  //
  // cam_setMode
  // cam_getMode
  // cam_setAWB
  // cam_getAWB
  // cam_setWBV
  // cam_getWBV
  // cam_setAEC
  // cam_getAEC
  // cam_setECV
  // cam_getECV
  // cam_setBrightness
  // cam_getBrightness
  // cam_setLightMode
  // cam_getLightMode
  // cam_testPattern
  // cam_getFrame
  // cam_setRegister
  // cam_getRegister
  //

#ifdef __cplusplus
}
#endif

#endif
