import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)

#waking up the module
ser.write(b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00')

turnAntenaOn = b'\x00\x00\xFF\x03\xFD\xD4\x14\x01\x17\x00'
ser.write(turnAntenaOn)

clear_buffer = ser.read(15)

def getBasicInfo(onlySAK):
    #InListPassiveTarget instruction
    listenerMode = b'\x00\x00\xFF\x04\xFC\xD4\x4A\x01\x00\xE1\x00'

    ser.write(listenerMode)
    #ingoring the first 6 bytes
    ser.read(6)

    #getting the type of card and its basic informations
    while(True):
        response = ser.read(100)
        if(response):
            if(onlySAK):
                return response[11], response[13 : 13 + response[12]]
            print('Basic card info: ', response.hex(' ').upper())
            ser.write(listenerMode)
            ser.read(6)

def getUsedTechnologyInfo():
    sak = getBasicInfo(True)