from can_jd import *
from axotec.gps import *
import numpy as np

#CAN
port = 'can1'
id = 10
can_jd = CANJD(port, id)    

#GPS
gps = GPS()


while True:
    speed = can_jd.get_speed_stimation()
    print(f"velocidad: {speed} m/s")


