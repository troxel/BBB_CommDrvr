#!/usr/bin/python3

import zmq
import random
import sys
import time
import os
from random import randint

from multiprocessing import Process, Pipe, current_process, active_children

from pprint import pprint

import signal
def sig_hdlr(sig, frame):
        print('You pressed Ctrl+C!')
        time.sleep(1)
        sys.exit(0)

signal.signal(signal.SIGINT, sig_hdlr)

# ---------------------------
def foo(port):

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:{}".format(port))

    print("port=",port)
    pprint(socket.bind)

    while(1):
       print("Worker {} waiting on a recv".format(port))
       message = socket.recv()
       print("Worker {} got message {}".format(port,message))

import comm

##port_lst = ("5000","5001","5002","5003","5004","5005","5006","5007")
port_lst = ("5000","5001")
comm_obj = comm.Comm()

proc_lst = [ {'target':comm_obj.incoming,'args':(), 'kwargs':{'port_lst':port_lst} },
             {'target':foo,'args':(),'kwargs':{'port':port_lst[0] } },
             {'target':foo,'args':(),'kwargs':{'port':port_lst[1] } } ]

pid_proc = {}

for proc in reversed(proc_lst):
    proc_obj =  Process(target=proc['target'],args=proc['args'], kwargs=proc['kwargs'])
    proc_obj.start()

    pid_proc[proc_obj.pid] = proc_obj


pprint(pid_proc)

if os.wait():
    print("Done")
    sys.exit()
