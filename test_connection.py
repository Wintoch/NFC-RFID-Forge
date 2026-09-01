import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(1)

ser.write(b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
time.sleep(0.1)

frimware_cmd = b'\x00\x00\xFF\x02\xFE\xD4\x02\x2A\x00'
print("Sending the frame")

ser.write(frimware_cmd)

time.sleep(0.1)

response = ser.read(100)
hex_response = response.hex(' ').upper()
print("Raw response:", hex_response)

ser.close