#!/usr/bin/python3

import zmq
import sys
import time
import os

# Central specification of the zmq ports
import msg_que

from multiprocessing import Process, active_children

from pprint import pprint

import signal
def sig_hdlr(sig, frame):
        print('You pressed Ctrl+C!')
        time.sleep(1)
        sys.exit(0)

signal.signal(signal.SIGINT, sig_hdlr)

import worker1

import comm
comm_obj = comm.Comm()

proc_lst = [ {'target':comm_obj.incoming,'args':(), 'kwargs':{} },
             {'target':comm_obj.outgoing,'args':(), 'kwargs':{} },
             {'target':worker1.translate,'args':(),'kwargs':{'port_in':msg_que.demux_lst[0],'port_out':msg_que.mux_lst[0] } },
             {'target':worker1.translate,'args':(),'kwargs':{'port_in':msg_que.demux_lst[1],'port_out':msg_que.mux_lst[1] } } ]

pid_proc = {}

# Start processes
for proc in reversed(proc_lst):
    proc_obj =  Process(target=proc['target'],args=proc['args'], kwargs=proc['kwargs'])
    proc_obj.start()

    pid_proc[proc_obj.pid] = proc_obj


pprint(pid_proc)

poller = zmq.Poller()

context_state = zmq.Context()
socket_state = context_state.socket(zmq.PAIR)
socket_state.bind("tcp://*:{}".format(msg_que.state))
poller.register(socket_state, zmq.POLLIN)

context_logger = zmq.Context()
socket_logger = context_state.socket(zmq.PAIR)
socket_logger.bind("tcp://*:{}".format(msg_que.logger))
poller.register(socket_logger, zmq.POLLIN)

# --- Start Polling Loop ----
while True:
   rdy = dict(poller.poll())
   for sock,event in rdy.items():
      pprint(sock)
      msg = sock.recv()
      print("\nchanging state",msg)




"""
if os.wait():
    print("Done")
    sys.exit()
"""
