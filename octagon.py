#!/usr/bin/python3

import zmq
import sys
import time
import os

# Central specification of the zmq ports
import msg_que

from multiprocessing import Process, Manager, active_children

from pprint import pprint

import signal
def sig_hdlr(sig, frame):
        print('You pressed Ctrl+C!')
        time.sleep(1)
        sys.exit(0)

signal.signal(signal.SIGINT, sig_hdlr)

if __name__ == "__main__":

   manager = Manager()
   import json

   state = manager.dict()
   state['time'] = time.time()

   import worker1

   import comm
   comm_obj = comm.Comm()

   dm = msg_que.demux_lst
   mx = msg_que.mux_lst

   proc_lst = [ {'target':comm_obj.incoming,'args':(), 'kwargs':{} },
                {'target':comm_obj.outgoing,'args':(), 'kwargs':{} },
                {'target':worker1.translate,'args':(),'kwargs':{'port_in':dm[0],'port_out':mx[0],'state':state } },
                {'target':worker1.translate,'args':(),'kwargs':{'port_in':dm[1],'port_out':mx[1],'state':state } } ]

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

   jid = open('./state.json', 'w')

   # --- Start Polling Loop ----
   while True:

      rdy = dict(poller.poll(1000))

      for sock,event in rdy.items():
         msg = sock.recv()
         print("msg received",msg)

      
      print(state['time'],"\n")
       
      print(json.dumps(dict(state)))
      jid.write(json.dumps(dict(state)))
      jid.flush()
      jid.seek(0)

"""
   if os.wait():
       print("Done")
       sys.exit()
"""
