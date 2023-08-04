import asyncio

from can_jd import *
from axotec.gps import GPS
import numpy as np

#CAN
port = 'can1'
id = 10
can_jd = CANJD(port, id)    

#GPS
gps = GPS()

async def speed_imu():
    # Inicializar la conexión al bus CAN
    # ...

    while True:
        # Leer datos del bus CAN
        speed_imu = await can_jd.get_speed_stimation()
        # Procesar datos del IMU
        # ...
        # Imprimir datos procesados
        print("Datos IMU:", speed_imu)

async def speed_gps():
    # Inicializar la conexión serial
    # ...

    while True:
        # Leer datos del GPS
        gps_data = await gps.get_vel()
        # Procesar datos del GPS
        # ...
        # Imprimir datos procesados
        print("Datos GPS:", gps_data)

async def main():
    # Crear tareas asincrónicas para leer IMU y GPS
    imu_task = asyncio.create_task(speed_imu())
    gps_task = asyncio.create_task(speed_gps())

    # Ejecutar tareas asincrónicas simultáneamente
    await asyncio.gather(imu_task, gps_task)

if __name__ == '__main__':
    # Iniciar bucle de eventos de asyncio
    asyncio.run(main())

