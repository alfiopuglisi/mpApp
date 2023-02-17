#!/usr/bin/env python

import time
from mpApp import mpManager
import multiprocessing


class MpMain():

    def __init__(self, mpConfig):
        self._mpConfig = mpConfig

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

        manager = mpManager.createMpManager(self._mpConfig.PORT, self._mpConfig.AUTHKEY, self._mpConfig.data, queues)

        # Prepare all processes
        for p in processes:
            p.create(manager=manager)

        # Launch everything
        for p in processes:

            a = multiprocessing.Process(target = p.run)
            b = multiprocessing.Process(target = p.server)
            a.start()
            b.start()

        while 1:
            time.sleep(1)


