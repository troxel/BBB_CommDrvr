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
   for m in msg:
      b_out = struct.pack('Bc',0xFc,m.encode())
      num = serial1.write(b_out)
      #print("wrote to {} num bytes {}".format(serial1_fspec,num))
   print("Done")
   time.sleep(7)
