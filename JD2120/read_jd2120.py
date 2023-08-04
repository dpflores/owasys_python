import canopen

import math

import os

import time

EDS_FILE = os.path.dirname(os.path.realpath(__file__)) +\
                           '/JD2xxx_v1.0.eds'
# Cargar archivo de configuración de dispositivo CANopen
network = canopen.Network()
network.connect(bustype='socketcan', channel='can1')
node_id = 10

node = network.add_node(node_id, EDS_FILE)

# for obj in node.object_dictionary.values():
#     print('0x%X: %s' % (obj.index, obj.name))
#     if isinstance(obj, canopen.objectdictionary.Record):
#         for subobj in obj.values():
#             print('  %d: %s' % (subobj.subindex, subobj.name))


# angulo en x: 0x6010
# angulo en y: 0x6020

# aceleracion en x: 0x3403
# aceleracion en y: 0x3404
# aceleracion en z: 0x3405

g = 9.81

resolution = g/1000

def test():
    x = node.sdo[0x3403].raw * resolution
    y = node.sdo[0x3404].raw * resolution
    z = node.sdo[0x3405].raw * resolution
    time.sleep(0.1)

    print(f'{{"x":{round(x,2)}, "y":{round(y,2)}, "z":{round(z,2)}}}')
# Acclerations
while True:
    

    test()
    # print(round(x,2), round(y,2), round(z,2))

# # Gyro
# while True:
#     x = node.sdo[0x3400].raw
#     y = node.sdo[0x3401].raw
#     z = node.sdo[0x3402].raw

#     print(round(x,2), round(y,2), round(z,2))

# X Y SLOPE
while True:
    x_slope = node.sdo[0x6010].raw

    y_slope = node.sdo[0x6020].raw

    print(round(x_slope,2), round(y_slope,2))


