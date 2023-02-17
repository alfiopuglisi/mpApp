#!/usr/bin/env python

import mpApp.mpManager

class MpProcess():
    '''
    Base class for an AO process
    '''

    def __init__(self, name, mpConfig):
        self._name = name
        self._mpConfig = mpConfig

    def create(self, port=-1, authkey='', host='localhost', manager=None, master=False):
        '''
        Creates the AO Client manager and related shared data
        '''
        if not manager:
            if master:
                self._manager = mpManager.createMpManager(port, authkey, self._mpConfig.data, self._mpConfig.modules.keys())
            else:
                self._manager = mpManager.createClientManager(host, port, authkey, self._mpConfig.data, self._mpConfig.modules.keys())
        else:
            self._manager = manager

        self._shareddata = {}
        for k in self._mpConfig.data.keys():
            self._shareddata[k] = getattr(self._manager, k).__call__()
        try:
            self._pipe_in  = getattr(self._manager, '%s_in'%self._name).__call__()
            self._pipe_out = getattr(self._manager, '%s_out'%self._name).__call__()
        except AttributeError:
            print( 'Warning: no command input to process %s' % self._name )
        self.prepare()

    def shared(self, name):
        return self._shareddata[name]

    def sendTo(self, dest, msg):
        self.outpipe(dest).send(msg)
 
    def outpipe(self, dest):
        return getattr(self._manager, '%s_out'%dest).__call__()

    def server(self):
        while True:
            msg = self._pipe_in.recv()
            tokens = msg.split()
            cmd = tokens[0]
            args = tokens[1:]
            try:
                retval = getattr(self, cmd).__call__(args)
            except AttributeError:
                retval = '%s: Unknown command %s' % (self._name, cmd)
            print(retval)
            self._pipe_in.send(retval)

    def prepare(self):
        pass

    def run( self):
        pass
