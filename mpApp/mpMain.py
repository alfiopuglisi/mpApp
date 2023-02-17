#!/usr/bin/env python

import time
from mpApp import mpManager
import multiprocessing


class MpMain():

    def __init__(self, mpConfig):
        self._mpConfig = mpConfig
        self._processes = []

    def run(self):

        classes = []
        queues = []

        for name, type in self._mpConfig.modules.items():
            m = __import__(type)
            cmd = 'm.%s%s(\'%s\', self._mpConfig)' % (type[0].upper(), type[1:], name)
            c = eval(cmd)
            classes.append(c)
            queues.append(name)

        # Start main manager

        manager = mpManager.createMpManager(self._mpConfig.PORT, self._mpConfig.AUTHKEY, self._mpConfig.data, queues)

        # Prepare all processes
        for c in classes:
            c.create(manager=manager)

        # Launch everything
        for c in classes:

            a = multiprocessing.Process(target = c.run)
            b = multiprocessing.Process(target = c.server)
            a.start()
            b.start()
            self._processes.append(a)
            self._processes.append(b)

        while 1:
            time.sleep(1)


