cmake_minimum_required(VERSION 3.16)
PROJECT(libfishcamp C CXX)

#***********************************************************
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/")
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../cmake_modules/")
include(GNUInstallDirs)
include(CMakeCommon)
find_package(INDI REQUIRED)

option(INDI_INSTALL_UDEV_RULES "Install UDEV rules" On)
option(INDI_INSTALL_FIRMWARE "Install Firmware" on)

include_directories( ${INDI_INCLUDE_DIR})

IF(APPLE)
  set(FIRMWARE_INSTALL_DIR "/usr/local/lib/indi/DriverSupport/fishcamp")
  ##This one is needed for homebrew
  include_directories( "/usr/local/include")
  ## This one is needed for Craft
  include_directories("${CMAKE_INSTALL_PREFIX}/include")
ELSE(APPLE)
  set(FIRMWARE_INSTALL_DIR "/lib/firmware" CACHE STRING "libfishcamp firmware installation dir")
  set(UDEVRULES_INSTALL_DIR "/lib/udev/rules.d" CACHE STRING "Base directory for udev rules")
ENDIF(APPLE)
#***********************************************************
find_package(USB1 REQUIRED)
include_directories( ${USB1_INCLUDE_DIR})
ADD_DEFINITIONS(-Wno-multichar)

set(LIBFISHCAMP_VERSION "1.1")
set(LIBFISHCAMP_SOVERSION "1")

set(fishcamp_LIB_SRCS fishcamp.c)

SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-error")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-error")

#build a shared library
ADD_LIBRARY(fishcamp SHARED ${fishcamp_LIB_SRCS})

set_target_properties(fishcamp PROPERTIES VERSION ${LIBFISHCAMP_VERSION} SOVERSION ${LIBFISHCAMP_SOVERSION})

target_link_libraries(fishcamp ${USB1_LIBRARIES})

INSTALL(FILES fishcamp.h fishcamp_common.h DESTINATION include/libfishcamp)

INSTALL(TARGETS fishcamp LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})

IF (INDI_INSTALL_FIRMWARE)
  install( FILES gdr_usb.hex Guider_mono_rev16_intel.srec DESTINATION ${FIRMWARE_INSTALL_DIR})
  IF(NOT APPLE AND INDI_INSTALL_UDEV_RULES)
    install(FILES 99-fishcamp.rules DESTINATION ${UDEVRULES_INSTALL_DIR})
  ENDIF()
ENDIF()
