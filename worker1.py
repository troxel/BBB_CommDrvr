#!/usr/bin/python3

import zmq
import sys
import time
import os

# Central specification of the zmq ports
import msg_que

# ---------------------------
def translate(port_in,port_out,state):

   context_state = zmq.Context()
   socket_state = context_state.socket(zmq.PAIR)
   socket_state.connect("tcp://localhost:{}".format(msg_que.state))
  
   context_in = zmq.Context()
   socket_in = context_in.socket(zmq.PAIR)
   print("Binding zmq at port {}".format(port_in) )
   socket_in.bind("tcp://*:{}".format(port_in))

   context_out = zmq.Context()
   socket_out = context_out.socket(zmq.PAIR)
   socket_out.connect("tcp://localhost:{}".format(port_out))

   while(1):
       message = socket_in.recv()
       print("Worker {} got message {}".format(port_in,message))
       socket_out.send(message)

       state['time'] = time.time() 

       ##socket_state.send(b'{pan:23.3}')
