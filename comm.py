#!/usr/bin/python

import zmq
import random
import sys
import time
import os
from random import randint
import os.path
import stat
import pprint
import serial
import select

import struct

class Comm:

   def __init__(self):

      self.serial_fspec = ['/dev/ttyUSB2','/dev/ttyO4']
      self.serial = [None]*len(self.serial_fspec)
      self.fds2ser = {}

      for inx in range(0,1):
         try:
            ### timeout parameter will have to be tuned...
            self.serial[inx] = serial.Serial(self.serial_fspec[inx],timeout=.2 )
         except Exception as err:
            print("Open error ",inx,self.serial_fspec[inx],err.args)
            sys.exit(0)

         # links file desc with serial object
         self.fds2ser[self.serial[inx].fileno()] = self.serial[inx]

      print("Opened {}".format(self.serial_fspec[inx]))

   # ---------------------------
   def init_ports(self,port_lst):

      # initialize mqz ports
      self.port_lst = port_lst
      self.socket_lst = [None]*len(port_lst)
      context = zmq.Context()

      for inx,port in enumerate(port_lst):
         self.socket_lst[inx] = context.socket(zmq.PAIR)
         self.socket_lst[inx].connect("tcp://localhost:{}".format(port_lst[inx]))
         print("Created zmq at port {} inx={}".format(port_lst[inx],inx) )


   # ---------------------------
   def incoming(self,port_lst):

      self.init_ports(port_lst)

      poller = select.poll()
      for inx in range(0,1):
         poller.register(self.serial[inx], select.POLLIN)

      # Begin loop...
      while True:

         print("polling")
         rdy_lst = poller.poll()

         for rdy in rdy_lst:
            fd = rdy[0]
            ser_obj = self.fds2ser[fd]

            msg_buffers = self._read_serial(ser_obj)

            for inx,msg in enumerate(msg_buffers):

               if msg:
                  print("msg{}-> {} inx={}".format(inx,msg.decode(),inx))
                  self.socket_lst[inx].send( msg )

   # ---------------------------
   def outgoing(self,port_lst):

      self.init_ports(port_lst)

      poller = zmq.Poller()
      for inx,sock from self.socket_lst:
         poller.register(sock, zmq.POLLIN)


      # Begin loop...
      while True:

         rdy = dict(poller.poll())


   # ---------------------------
   def _read_serial(self,ser_obj):

      msg_buffers = [bytearray(),bytearray(),bytearray(),bytearray()]

      while(1):
         bytes_in = ser_obj.read(2)

         if len(bytes_in) == 0:
            return(msg_buffers)

         if len(bytes_in) != 2:
            print("Opps increase timeout {}".format(len(bytes_in)) )
            time.sleep(1)
            ser_obj.read(1)
            continue

         if bytes_in[0] == 0xFC:
            msg_buffers[0].append(bytes_in[1])
         elif bytes_in[0] == 0xFD:
            msg_buffers[1].append(bytes_in[1])
         elif bytes_in[0] == 0xFE:
            msg_buffers[2].append(bytes_in[1])
         elif bytes_in[0] == 0XFF:
            msg_buffers[3].append(bytes_in[1])
         else:
            # Must be out of sync
            print('OUT OF SYNC')
            byte = ser_obj.read(1)

         ##print("len ->",len(bytes_in),bytes_in)


"""
context = zmq.Context()

for inx in range(2):
    socket_lst[inx] = context.socket(zmq.PAIR)
    socket_lst[inx].bind("tcp://*:{}".format(port_lst[inx]))

    print('init {}'.format(inx))

inx = 0
while True:
    rnd = randint(0, 1)
    print("Sending message to {}".format(rnd))
    send_msg = 'Hello worker {}'.format(rnd)
    socket_lst[rnd].send( str.encode(send_msg) )
    print("sent!")
    time.sleep(3)

while(1):
    print("polln")
    socks = dict(poller.poll())

    for key, value in socks.items():
        print("key {} : value {}".format(key,value))


 # ---------------------------
   def ser_mon(self,ser_port):

      ser_obj = self.serial[0]

      while(1):

         message = self._read_serial(ser_obj)
         inx=0
         for msg in message:
            print("message-> ",msg.decode("utf-8"),inx)
            inx =+ 1
            ##print("msg --> {}".format(message))

            ##rnd = randint(0, len(port_lst)-1 )
            ##print("Sending message to worker {}".format(port_lst[rnd]))
            ##send_msg = 'Hello worker {}'.format(port_lst[rnd])
            ##socket_lst[rnd].send( str.encode(send_msg) )
            ##time.sleep(3)

"""
