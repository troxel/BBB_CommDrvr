#!/usr/bin/python

import zmq
import sys
import time
import os
import os.path
from pprint import pprint
import serial
import select
import struct

import msg_que

class Comm:

   def __init__(self):

      # Serial file handles are preserved across fork
      self.serial_fspec = ['/dev/ttyO1','/dev/ttyO4']
      self.serial_fspec = ['/dev/ttyUSB2']
      self.serial = [None]*len(self.serial_fspec)
      self.fds2ser = {}   # file descriptor to serial device
      self.fds2dtm = {}   # file descriptor to serial port number datum 

      for inx,fspec in enumerate(self.serial_fspec):
         try:
            ### timeout parameter will have to be tuned to hardware...
            self.serial[inx] = serial.Serial(self.serial_fspec[inx],timeout=.23 )
         except Exception as err:
            print("Open error ",inx,self.serial_fspec[inx],err.args)
            sys.exit(0)

         # links file desc with serial object
         fileno = self.serial[inx].fileno()
         self.fds2ser[fileno] = self.serial[inx]
         self.fds2dtm[fileno] = inx * 4

      print("Opened {}".format(self.serial_fspec[inx]))

   # ---------------------------
   # Receives incoming muxed data from serial ports
   # and demuxes and distributes to the appropiate msg queue
   # ---------------------------
   def incoming(self):

      client_ports = msg_que.demux_lst

      # initialize client side zmq sockets
      self.client_socks = [None]*len(client_ports)
      context = zmq.Context()

      for inx,port in enumerate(client_ports):
         self.client_socks[inx] = context.socket(zmq.PAIR)
         self.client_socks[inx].connect("tcp://localhost:{}".format(client_ports[inx]))
         print("Created zmq at port {} inx={}".format(client_ports[inx],inx) )

      # Register serial port with poller
      poller = select.poll()
      for inx in range(0,1):
         poller.register(self.serial[inx], select.POLLIN)

      # --- Start Polling Loop ----
      while True:


         rdy_lst = poller.poll()
         # returns a list of truples - (fd,event).
         for rdy in rdy_lst:

            # File descriptor
            fd = rdy[0]  
            ser_obj = self.fds2ser[fd]
            datum = self.fds2dtm[fd]

            msg_buffers = self._read_serial(ser_obj)

            for inx,msg in enumerate(msg_buffers):
               if msg:
                  self.client_socks[inx+datum].send( msg )

   # ---------------------------
   # Receives outgoing date from msg queue and muxes the data
   # and sends out the serial port.
   # ---------------------------
   def outgoing(self):

      server_ports = msg_que.mux_lst

      # initialize server zmq sockets
      self.server_ports = server_ports
      self.server_socks = [None]*len(server_ports)
      context = zmq.Context()

      for inx,port in enumerate(server_ports):
         self.server_socks[inx] = context.socket(zmq.PAIR)
         print("Binding zmq at port {} inx={}".format(server_ports[inx],inx) )
         self.server_socks[inx].bind("tcp://*:{}".format(server_ports[inx]))

      poller = zmq.Poller()
      for inx,sock in enumerate(self.server_socks):
         poller.register(sock, zmq.POLLIN)

      # --- Start Polling Loop ----
      while True:
         rdy = dict(poller.poll())
         for sock,event in rdy.items():
            msg = sock.recv()
            #time.sleep(2)
            #smsg = ['Y','Y']
            #for m in smsg:
            #   b_out = struct.pack('Bc',0xFc,m.encode())
            #   self.serial[0].write(b_out)
            print("\nGot !!!!",msg)

         ##pprint(rdy)


   # ---------------------------
   def _read_serial(self,ser_obj):

      msg_buffers = [bytearray(),bytearray(),bytearray(),bytearray()]

      while(1):
         bytes_in = ser_obj.read(2)

         if len(bytes_in) == 0:
            return(msg_buffers)

         if len(bytes_in) != 2:
            print("Opps increase timeout only read {} byte".format(len(bytes_in)) )
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
