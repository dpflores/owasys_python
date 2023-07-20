from ctypes import *
libIO=cdll.LoadLibrary("libIOs_Module.so")      # Para el manejo de las entradas y salidas
libRTU=cdll.LoadLibrary("libRTU_Module.so")     # Para los sensores integrados del OWASYS
libGPS=cdll.LoadLibrary("libGPS2_Module.so")    # Para el manejo del GPS

LED_OFF = 0
LED_ON = 1

def start_gps():
    
    # 0: GPS module control, 1: user control
    libGPS.GPS_Set_Led_Mode(0)

def main():
    start_gps()
if __name__ == "__main__":
    main()
