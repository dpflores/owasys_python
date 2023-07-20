#!/usr/bin/python

from ctypes import *
libIo=cdll.LoadLibrary("libIOs_Module.so")
libRtu=cdll.LoadLibrary("libRTU_Module.so")

libIo.IO_Initialize()
libIo.IO_Start()
libRtu.RTUControl_Initialize()
libRtu.RTUControl_Start()

print("Encendiendo Todos los LEDS")
ledOn = 1
libIo.DIGIO_Set_LED_SW0(ledOn)
libIo.DIGIO_Set_LED_SW1(ledOn)
libIo.DIGIO_Set_LED_SW2(ledOn)
libIo.DIGIO_Set_PPS_GPS(ledOn)


versionIo = create_string_buffer(32) # create a 32 byte buffer, initialized to NUL bytes
libIo.IO_GetVersion.argtypes=[c_char_p]
libIo.IO_GetVersion(versionIo)
print("libIOs version: " + str(versionIo.value)) 

versionRtu = create_string_buffer(32) # create a 32 byte buffer, initialized to NUL bytes
libRtu.RTUControl_GetVersion.argtypes=[c_char_p]
libRtu.RTUControl_GetVersion(versionRtu)
print("libRTU version: " + str(versionRtu.value))

ad_temp = c_int()
libRtu.RTUGetAD_TEMP.argtypes=[POINTER(c_int)]
libRtu.RTUGetAD_TEMP(byref(ad_temp))
print("Temperature: " + str(ad_temp.value) + "C")

libIo.IO_Finalize()
libRtu.RTUControl_Finalize()