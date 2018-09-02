import sys
import time
import os

import serial
import struct

serial1_fspec = '/dev/ttyUSB2'
try:
    serial1 = serial.Serial(serial1_fspec, os.O_RDWR)
except Exception as e:
    print("Open error ",serial1_fspec,e.message,e.args)
    sys.exit(0)

print("fd ",serial1)

while(1):

   msg = ['t','e','s','t',' ','t','h','i','s']
   bytes_out1 = bytes()
   for m in msg:
      b_out = struct.pack('Bc',0xFc,m.encode())
      bytes_out1 += b_out
      
   num = serial1.write(bytes_out1)
   ##print("wrote to {} num bytes {}".format(serial1_fspec,num))

      #time.sleep(1)
   bytes_out2 = bytes()
   for m in msg:
      b_out = struct.pack('Bc',0xFd,m.encode())
      bytes_out2 += b_out

   num = serial1.write(bytes_out2)

   print("Done")
   time.sleep(7)
