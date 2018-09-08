#!/usr/bin/python3

import zmq
import sys
import time
import os

from multiprocessing import Process, Manager, active_children

from pprint import pprint

# ------- signal handler --------------
import signal
pid = os.getpid()
def sig_hdlr(sig, frame):
   if pid == os.getpid():
      print('Interrupted !')
   sys.exit(0)

signal.signal(signal.SIGINT, sig_hdlr)
# --------------------------------------

# Central specification of the zmq ports
import msg_que

import zlog

if __name__ == "__main__":

   import logging

   manager = Manager()
   import json

   state = manager.dict()
   state['time'] = time.time()
   state['log_lvl'] = zlog.DEBUG

   import worker1

   import comm
   comm_obj = comm.Comm()

   # short cuts
   dm = msg_que.demux_lst
   mx = msg_que.mux_lst

   proc_lst = [ {'target':comm_obj.incoming,'args':(), 'kwargs':{'state':state },'name':'incoming' },
                {'target':comm_obj.outgoing,'args':(), 'kwargs':{'state':state },'name':'outgoing' },
                {'target':worker1.translate,'args':(),'kwargs':{'port_in':dm[0],'port_out':mx[2],'state':state },'name':'translator1' },
                {'target':worker1.translate,'args':(),'kwargs':{'port_in':dm[1],'port_out':mx[2],'state':state },'name':'translator2' } ]

   pid_proc = {}

   # Start processes
   for proc in reversed(proc_lst):
       proc_obj =  Process(target=proc['target'],args=proc['args'], kwargs=proc['kwargs'], name=proc['name'])
       proc_obj.start()

       pid_proc[proc_obj.pid] = proc_obj


   poller = zmq.Poller()
   context = zmq.Context()

   # state not used, using Manager instead
   #socket_state = context.socket(zmq.PAIR)
   #socket_state.bind("tcp://*:{}".format(msg_que.state))
   #poller.register(socket_state, zmq.POLLIN)

   socket_logger = context.socket(zmq.PAIR)
   socket_logger.bind("tcp://*:{}".format(msg_que.logger))
   poller.register(socket_logger, zmq.POLLIN)

   jid = open('./state.json', 'w')

   # --- Start Polling Loop ----

   proc_cnt = len(active_children())
   print("Number of Subprocesses {}".format(proc_cnt))
   while True:

      rdy = dict(poller.poll(2000))

      for sock,event in rdy.items():
         msg = sock.recv()
         print(msg.decode())

      # Maintain state file
      jid.write(json.dumps(dict(state)))
      jid.flush()
      jid.seek(0)

      # If any subprocess has exited then stop the rest
      # In production systemd will restart if the main process dies
      if len(active_children()) < proc_cnt:
         for pid,proc in pid_proc.items():
            print("Stopping ",proc.name)
            proc.terminate()
         break

   print("Done")
   exit(0)
