#!/usr/bin/env python

import multiprocessing
import multiprocessing.managers
from mpApp.mpTypes import SharedBuf


def createMpManager(port, authkey, shareddata={}, pipes=[]):
    '''
    Create a manager object with all shareable data.
    data is a dictionary of 'name': desc
    where desc is a namedtuple containing shape and dtype elements.
    '''

    class MpManager(multiprocessing.managers.SyncManager):
        pass

    aodata = {}
    pipes_in = {}
    pipes_out = {}

    # Use set() to remove duplicates
    for p in set(pipes):
        print('Registering pipe: ', p)
        pipes_in[p], pipes_out[p] = multiprocessing.Pipe()
        MpManager.register(p+'_in', lambda v=pipes_in[p]: v)
        MpManager.register(p+'_out', lambda v=pipes_out[p]: v)

    for k, v in shareddata.items():
        print('Registering new array: ', k, v)
        aodata[k] = SharedBuf(v)
        MpManager.register(k, lambda v=aodata[k]: v)   # Use default lambda value to bind

    manager = MpManager(address=('', port), authkey=authkey)
    manager.start()
    print('MpManager started on port %d' % port)
    return manager


def createClientManager(remote_host, port, authkey, shareddata={}, pipes=[]):
    '''
    Create a client manager to access shared objects remotely
    '''
    class MpClientManager(multiprocessing.managers.SyncManager):
        pass

    for k, v in shareddata.items():
        MpClientManager.register(k)

    # Use set() to remove duplicates
    for p in set(pipes):
        MpClientManager.register(p+'_in')
        MpClientManager.register(p+'_out')

    manager = MpClientManager(address=(remote_host, port), authkey=authkey)
    manager.connect()

    print('MpClientManager connected to %s:%d' % (remote_host, port))
    return manager

# ___oOo___
