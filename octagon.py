import os
import time
import sys
import select

class Comm(object):

    def __init__(self):

        import os
        self.channels = range(0,8)
        self.port_in = []
        self.port_out = []

        for fifo in self.channels:

            # input
            print("Test->{}".format(fifo) )


            fifo_name = "./fifos/demux_in_{}".format(fifo)
            print("Making {}".format(fifo_name))
            if not os.path.exists(fifo_name):
                os.mkfifo(fifo_name)

            self.port_in.append(os.open(fifo_name, os.O_RDONLY | os.O_NONBLOCK))
            # output
            fifo_name = "./fifos/mux_out_{}".format(fifo)

            if not os.path.exists(fifo_name):
                os.mkfifo(fifo_name)

            print(">>{}".format(fifo_name))

            fd = os.open(fifo_name, os.O_WRONLY | os.O_NONBLOCK)


            self.port_out.append(fd)









'''
def child( ):
    pipeout = os.open(pipe_name, os.O_WRONLY)
    counter = 0
    while True:
        time.sleep(1)
        os.write(pipeout, 'Number %03d\n' % counter)
        counter = (counter+1) % 5

def parent( ):
    pipein = open(pipe_name, 'r')
    while True:
        line = pipein.readline()[:-1]
        print 'Parent %d got "%s" at %s' % (os.getpid(), line, time.time( ))

if not os.path.exists(pipe_name):
    os.mkfifo(pipe_name)
pid = os.fork()
if pid != 0:
    parent()
else:
    child()
'''
