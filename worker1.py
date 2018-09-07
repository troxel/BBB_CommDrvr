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

   socket_log = context.socket(zmq.PAIR)
   socket_log.connect("tcp://localhost:{}".format(msg_que.logger))

   socket_in = context.socket(zmq.PAIR)
   socket_in.bind("tcp://*:{}".format(port_in))

   socket_out = context.socket(zmq.PAIR)
   socket_out.connect("tcp://localhost:{}".format(port_out))

   while(1):
       message = socket_in.recv()
       print("Worker {} got message {}".format(port_in,message))
       socket_out.send(message)

       state['time'] = time.time()
