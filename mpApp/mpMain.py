#!/usr/bin/env python

import sys
import time
import signal
from mpApp import mpManager
import multiprocessing


class MpMain():

    def __init__(self, mpConfig):
        self._mpConfig = mpConfig
        signal.signal(signal.SIGTERM, self.exit)

    def run(self):

        processes = []
        queues = []

        for name, type in self._mpConfig.modules.items():
            m = __import__(type)
            classname = type[0].upper() + type[1:]
            classtype = getattr(m, classname)
            process = classtype(name, self._mpConfig)
            processes.append(process)
            queues.append(name)

        # Start main manager
        manager = mpManager.createMpManager(self._mpConfig.PORT,
                                            self._mpConfig.AUTHKEY,
                                            self._mpConfig.data,
                                            queues)

        # Prepare all processes
        for p in processes:
            p.create(manager=manager)

        # Launch everything
        self.allprocs = []
        for p in processes:
            a = multiprocessing.Process(target=p.run)
            b = multiprocessing.Process(target=p.server)
            a.start()
            b.start()
            self.allprocs.append(a)
            self.allprocs.append(b)

        while True:
            time.sleep(1)

    def exit(self, *args):
        for p in self.allprocs:
            p.terminate()
        sys.exit(0)

# ___oOo___
