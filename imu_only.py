#! /usr/bin/env python
"""
A skeleton python script which reads GNSS position from libGPS2
"""
import logging

import json

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)-10s: [%(lineno)d] %(message)s',
                    level=logging.INFO)
logger.setLevel(logging.INFO)

from ctypes import *
import termios
import logging
import time

from ctypes import  (CDLL, Union, Structure, POINTER, cast, byref, create_string_buffer, sizeof,
                     c_ubyte, c_short, c_uint, c_ulong, c_int, c_long, c_float,
                     c_double, c_longlong, c_char, c_byte, c_ushort)

SLEEP_TIME = 1

class TGPS_MODULE_CONFIGURATION (Structure):
    _fields_ = [("DeviceReceiverName",  c_char * 20),
               ("ParamBaud", c_uint),
               ("ParamParity", c_int),
               ("ParamLength", c_ubyte),
               ("ProtocolName", c_char * 10),
               ("GPSPort", c_ubyte),
               ]
    def __init__(self,
        DeviceReceiverName=b'GPS_UBLOX',
        ParamBaud=c_uint(termios.B115200), #B115200
        ParamParity=c_int(termios.IGNPAR), #IGNPAR
        ParamLength=c_ubyte(termios.CS8), #CS8
        ProtocolName=b'NMEA',
        GPSPort=c_ubyte(0)): # COM1
        super(TGPS_MODULE_CONFIGURATION, self).__init__(DeviceReceiverName,
            ParamBaud, ParamParity, ParamLength,
            ProtocolName, GPSPort)

class TGPS_COORD (Structure):
    _fields_ = [("Degrees",  c_ushort),
                ("Minutes", c_ubyte),
                ("Seconds", c_double),
                ("Dir", c_byte)
               ]

class TPOSITION_DATA (Structure):
    _fields_ = [("PosValid",  c_ubyte),
                ("OldValue", c_ubyte),
                ("Latitude", TGPS_COORD),
                ("Longitude", TGPS_COORD),
                ("Altitude", c_double),
                ("NavStatus [3]", c_char * 3),
                ("HorizAccu", c_double),
                ("VertiAccu", c_double),
                ("Speed", c_double),
                ("Course", c_double),
                ("HDOP", c_double),
                ("VDOP", c_double),
                ("TDOP", c_double),
                ("numSvs", c_ubyte),
                ("LatDecimal", c_double),
                ("LonDecimal", c_double)
               ]

class MOVE_INT_T (Structure):
    _fields_ = [("scale", c_ubyte),
                ("x_axis", c_double),
                ("y_axis", c_double),
                ("z_axis", c_double)
                ]


def getdict(struct):
    result = {}
    for field, _ in struct._fields_:
         value = getattr(struct, field)
         # if the type is not a primitive and it evaluates to False ...
         if (type(value) not in [int, float, bool]) and not bool(value):
             # it's a null pointer
             value = None
         elif hasattr(value, "_length_") and hasattr(value, "_type_"):
             # Probably an array
             value = list(value)
         elif hasattr(value, "_fields_"):
             # Probably another struct
             value = getdict(value)
         result[field] = value
    return result

# IOs class
class IOs:
    def __init__(self):
        self.libIo=cdll.LoadLibrary("libIOs_Module.so")
        self.libIo.IO_Initialize()
        self.libIo.IO_Start()

        versionIo = create_string_buffer(32)
        self.libIo.IO_GetVersion.argtypes=[c_char_p]
        self.libIo.IO_GetVersion(versionIo)
        # logging.debug("libIOs version: %s", versionIo.value.decode('utf-8'))


    def set_led1(self):
        # logging.info("Switching LED1 on")
        ledOn = 1
        self.libIo.DIGIO_Set_LED_SW1(ledOn)

    def __del__(self):
        self.libIo.IO_Finalize()
        # logging.info("IO object deleted")

# RTU class
class RTU:
    def __init__(self):
        self.libRtu=cdll.LoadLibrary("libRTU_Module.so")
        self.libRtu.RTUControl_Initialize()
        self.libRtu.RTUControl_Start()
        versionRtu = create_string_buffer(32)
        self.libRtu.RTUControl_GetVersion.argtypes=[c_char_p]
        self.libRtu.RTUControl_GetVersion(versionRtu)

        self.acceldata = None

        self.accel_init()
       
    
    def accel_init(self):

        # self.libRtu.RTU_CfgMovementSensor.argtypes=[c_ubyte, c_ubyte, c_ubyte, POINTER(MOVE_INT_T)]
        self.libRtu.RTU_CfgMovementSensor.restype = c_int
        
        self.movehandler = MOVE_INT_T()
        self.pmovehandler = pointer(self.movehandler)

        
        while True:
            #ret = self.libRtu.RTU_CfgMovementSensor(c_ubyte(0),c_ubyte(100),c_ubyte(50),self.pmovehandler)
            ret = self.libRtu.RTU_CfgMovementSensor(1, 0, 0, self.pmovehandler)
            logging.info(ret)
            if ret != 0:
                break
                # ret = self.libGps.GPS_Finalize()
                time.sleep(5)   
            else:
                break
        
        self.set_accel()
        logging.info("Modulo iniciado correctamente")

    def set_accel(self):
        self.libRtu.RTU_GetRawAcceleration.restype = c_int
        self.libRtu.RTU_GetRawAcceleration.argtypes=[POINTER(MOVE_INT_T)]
        self.acceldata = MOVE_INT_T()
        self.pacceldata= pointer(self.acceldata)
        
    def get_adtemp(self):
        ad_temp = c_int()
        self.libRtu.RTUGetAD_TEMP.argtypes=[POINTER(c_int)]
        self.libRtu.RTUGetAD_TEMP(byref(ad_temp))
        # logging.info("Temperature: %d C", ad_temp.value)

    def get_raw_accel(self):
        ret = self.libRtu.RTU_GetRawAcceleration(self.pacceldata)
        if (ret == 0):
            return getdict(self.acceldata)
        return ret


    def __del__(self):
        self.libRtu.RTUControl_Finalize()
        # logging.info("RTU object deleted")

# GNSS class
class GNSS:
    def __init__(self, io=None, rtu=None):
        ret = c_int(0)
        self.io = io or IOs()
        self.rtu = rtu or RTU()
        self.libGps=cdll.LoadLibrary("libGPS2_Module.so")
        self.gpsactive = False
        self.gpsdata = None

        self.gps_init()

    def gps_init(self):
        gpsconf=TGPS_MODULE_CONFIGURATION()
        pgpsconf = pointer(gpsconf)
        self.libGps.GPS_Initialize.restype = c_int
        ret = self.libGps.GPS_Initialize(pgpsconf)

        

        self.libGps.GPS_Start.restype = c_int
        while True:
            ret = self.libGps.GPS_Start()
            ## ADDED
            # 0: GPS module control, 1: user control.
            self.libGps.GPS_Set_Led_Mode(0)
            
            # 0: Normal, 1: Fast Acquisition, 2: High Sensitivity (Default value)
            self.libGps.GPS_SetGpsMode(0)

            if ret != 0:
                ret = self.libGps.GPS_Finalize()
                time.sleep(5)   
            else:
                break

        self.gpsactive = c_int()
        self.libGps.GPS_IsActive.argtypes=[POINTER(c_int)]
        self.libGps.GPS_IsActive(byref(self.gpsactive))
        # logging.debug(f"Is GPS active? {'Yes' if self.gpsactive else 'No'}")
        # logging.info("GPS-> Module initialized & started")

        self.set_pos()

    def set_pos(self):
        self.libGps.GPS_GetAllPositionData.restype = c_int
        self.libGps.GPS_GetAllPositionData.argtypes=[POINTER(TPOSITION_DATA)]
        self.gpsdata = TPOSITION_DATA()
        self.pgpsdata = pointer(self.gpsdata)

    def set_measurement_rate(self, measRate):
        try:
            measRate=int(measRate)
        except ValueError:
            # logging.error("This is not a whole number.")
            pass
        if measRate != 1 and measRate != 2 and measRate != 4:
            # logging.error(f"The value ({measRate}) is out of range")
            pass
            return
        # logging.info(f"Setting Measurement Rate to {measRate} Hz")
        rate = c_char(measRate)
        self.libGps.GPS_SetMeasurementRate.argtypes=[c_char]
        self.libGps.GPS_SetMeasurementRate(rate)

    def get_pos(self):
        ret = self.libGps.GPS_GetAllPositionData(self.pgpsdata)
        if (ret == 0):
            return getdict(self.gpsdata)
        return ret

    def __del__(self):
        self.libGps.GPS_Finalize()
        del self.io
        del self.rtu

        # logging.info("GNSS object deleted")


def main():

    # Power State

    rtu = RTU()

    # This is just an example, do whatever you do
    t_end = time.time() + 60 * 15
    while True:
        data = rtu.get_raw_accel()
        # logger.info(f"Position: {data}")
        print(data)
        # print(json.dumps(data_string))
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()