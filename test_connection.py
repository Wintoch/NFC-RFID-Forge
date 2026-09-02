import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)

##### SHORT COMMAND ASKING FOR OS VERSION

ser.write(b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

frimware_cmd = b'\x00\x00\xFF\x02\xFE\xD4\x02\x2A\x00'
print("Sending the frame")

ser.write(frimware_cmd)

response = ser.read(100)
hex_response = response.hex(' ').upper()
print("Raw response:", hex_response)

ser.close