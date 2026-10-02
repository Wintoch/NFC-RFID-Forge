import serial
import time

ser = serial.Serial('COM3', 115200, timeout=0.05)

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
    sak, uid = getBasicInfo(True)
    match sak:
        case 0x08:
            readMifare1k(uid)
        case _:
            print("circuit not supported yet")
            
def writeCorrectFrame(middleFromMessage):
    controlSum = sum(middleFromMessage)
    dcs = (256-(controlSum % 256)) % 256
    controlLen = len(middleFromMessage)
    lcs = (256-(controlLen % 256)) % 256
    frame = b'\x00\x00\xFF'+ bytes([controlLen]) + bytes([lcs]) + middleFromMessage + bytes([dcs]) + b'\x00'
    ser.write(frame)
    ser.read(6)
            
def readMifare1k(uid):
    fabricKey = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    for x in range(0,64,4):
        middle = bytearray(b'\xD4\x40\x01\x60')
        middle.append(x)
        middle.extend(fabricKey)
        middle.extend(uid)
        
        writeCorrectFrame(middle)
        
        checkStatus = ser.read(20)
        authorizationStatus = checkStatus[7]
                
        if (authorizationStatus == 0x14):
            print('Status 0x14')
            getBasicInfo(True)
            continue
        elif (authorizationStatus == 0x00):
            for i in range(4):    
                middleAccept = bytearray(b'\xD4\x40\x01\x30')
                middleAccept.append(x + i)
                writeCorrectFrame(middleAccept)
                
                blockData = ser.read(30)[8:24].hex(' ').upper()
                print('Block number: ', x + i, '    ', blockData )
            
        
getUsedTechnologyInfo()