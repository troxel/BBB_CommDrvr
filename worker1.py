#!/usr/bin/python3

import zmq
import sys
import time
import os

# Central specification of the zmq ports
import msg_que

import zlog

# ---------------------------
def translate(port_in,port_out,state):

   context = zmq.Context()

   socket_log = context.socket(zmq.PAIR)
   socket_log.connect("tcp://localhost:{}".format(msg_que.logger))

   socket_in = context.socket(zmq.PAIR)
   if state['log_lvl'] <= zlog.DEBUG :
      socket_log.send("Binding zmq at port {}".format(port_in).encode() )
   socket_in.bind("tcp://*:{}".format(port_in))

   socket_out = context.socket(zmq.PAIR)
   if state['log_lvl'] <= zlog.DEBUG :
      socket_log.send("Connecting to output at port {}".format(port_out).encode() )
   socket_out.connect("tcp://localhost:{}".format(port_out))

   if state['log_lvl'] <= zlog.DEBUG :
      socket_log.send("Working waiting on port {}".format(port_in).encode() )
   while(1):
       message = socket_in.recv()
       print("Worker {} got message {}".format(port_in,message))
       socket_out.send(message)

       state['time'] = time.time()

       ##socket_state.send(b'{pan:23.3}')
