import serial
import time

ser = serial.Serial('COM4', 115200, timeout=0.2)

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
        case 0x20:
            readSmartCard()
        case 0x28:
            readSmartCard()
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
                
        if (authorizationStatus == 0x00):
            for i in range(4):    
                middleAccept = bytearray(b'\xD4\x40\x01\x30')
                middleAccept.append(x + i)
                writeCorrectFrame(middleAccept)
                
                blockData = ser.read(30)[8:24].hex(' ').upper()
                print('Block number: ', x + i, '    ', blockData )
        elif (authorizationStatus == 0x14):
                    print('Status 0x14')
                    getBasicInfo(True)

# Sends an APDU frame to the card, locates the target EMV tag (TLV format) in the response,
# and returns the extracted data payload along with its length.
def cutSmartResponse(msgToSend, toFind,):
    writeCorrectFrame(msgToSend)
    response = ser.read(255)
    start = response.find(toFind) + (len(toFind) - 1)
    length = response[start+1]
    start+=2
    end = start+length
    value = response[start:end]
    return value, length


def readSmartCard():
    header = bytearray(b'\xD4\x40\x01\x00\xA4\x04\x00\x0E' + b'2PAY.SYS.DDF01' + b'\x00')
    address, length = cutSmartResponse(header, b'\x4F')
    
    basicInfo = bytearray(b'\xD4\x40\x01\x00\xA4\x04\x00'+ bytes([length]) + address + b'\x00')
    cardName = cutSmartResponse(basicInfo, b'\x50')
    print(cardName[0].decode('ascii'))
    
    
    # cardNumber = bytearray(b'\xD4\x40\x01\x80\xA8\x00\x00\x23\x83\x21' + b'\x26\x00\x00\x00' + b'\x00' * 29 + b'\x00')
    for x in range(1,6):
        for y in range(1,6):
            cardNumberMSG = bytearray(b'\xD4\x40\x01' + b'\x00\xB2' + bytes([y]) + bytes([(x << 3) | 4]) + b'\x00')
            writeCorrectFrame(cardNumberMSG)
            response = ser.read(255)
            toSearch = (b'\x5A\x08', b'\x57\x13')
            for tag in toSearch:
                if(tag in response):
                    where = response.find(tag)
                    cardNumber = response[where+2:where+10]
                    print("Card number: " , cardNumber.hex(' ').upper())
                    break
            tag = b'\x5F\x24'
            if(tag in response):
                where = response.find(tag)
                cardExpiry = response[where+3:where+5]
                print("Card expiry date(yy/mm): " , cardExpiry.hex('/').upper())
                break
    
    #reading the usage count
    usageCountMSG = bytearray(b'\xD4\x40\x01' + b'\x80\xCA' + b'\x9F\x36' + b'\x00')
    writeCorrectFrame(usageCountMSG)
    print(ser.read(255).hex(' ').upper())
    usageCount = cutSmartResponse(usageCountMSG, b'\x9F\x36')
    print("This card was used this many times:" , int.from_bytes(usageCount[0], 'big'))
    

getUsedTechnologyInfo()