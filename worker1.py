#!/usr/bin/python3

import zmq
import sys
import time
import os

# Central specification of the zmq ports
import msg_que

# ---------------------------
def translate(port_in,port_out,state):

   context = zmq.Context()

   sock_log = context.socket(zmq.PAIR)
   sock_log.connect("tcp://localhost:{}".format(msg_que.logger))

   # Receiving
   sock_in = context.socket(zmq.PAIR)
   sock_in.bind("tcp://*:{}".format(port_in))

   # Self same comm port as receiving
   sock_same = context.socket(zmq.PAIR)
   sock_same.connect("tcp://localhost:{}".format(port_in+100))

   # Destination port
   sock_out = context.socket(zmq.PAIR)
   sock_out.connect("tcp://localhost:{}".format(port_out))

   while(1):
       message = sock_in.recv()
       ##print("Worker {} got message {}".format(port_in,message))

       # Ack or respond to receiving port
       sock_same.send(b'Ack')

       # Send to Destination
       sock_out.send(message)

       state['time'] = time.time()
