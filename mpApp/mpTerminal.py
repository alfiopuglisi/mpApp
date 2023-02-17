#!/usr/bin/env python

import time
import multiprocessing
import numpy as np

from mpProcess import MpProcess

class Terminal(MpProcess):

    def __init__(self, name, mpConfig):
        MpProcess.__init__(self, name)
        self._mpConfig = mpConfig

    def run(self):
        self._pipes={}
        for m in self.mpConfig.modules.keys():
            self._pipes[m] = getattr(self._manager,'%s_out'%m).__call__()
        while 1:
            gotsomething=False
            for p in self._pipes.keys():
                if self._pipes[p].poll():
                    obj = self._pipes[p].recv()
                    print('%s says: %s' % (p, str(obj)))
                    gotsomething=True 
            if not gotsomething:
                time.sleep(0.1)
 
    def server( self):
        while 1:
            try:
                line = sys.__stdin__.readline()
                # empty line == EOF
                if line=='':
                     sys.exit(0)
               
                dest, cmd = line.strip().split(None, 1)
                self.sendTo( dest, cmd)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)


if __name__ == '__main__':

    a = Terminal('terminal')
    a.create( aoconfig.PORT, aoconfig.AUTHKEY, 'localhost')

    output = multiprocessing.Process( target = a.run)
    output.start()

    a.server()
