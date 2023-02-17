#!/usr/bin/env python

import multiprocessing
#import multiprocessing.managers
import multiprocessing.sharedctypes
import ctypes
import numpy as np


class MpStructure(ctypes.Structure):
    '''
    Uses np.ctypeslib to convert any ndarray get/set
    into a ctypes.Array.
    '''
    def __setattr__(self, name, value):
        if isinstance(value, np.ndarray):
            value = np.ctypeslib.as_ctypes(value)
        ctypes.Structure.__setattr__(self, name, value)

    def __getattribute__(self, name):
        value = ctypes.Structure.__getattribute__(self, name)
        if isinstance(value, ctypes.Array):
            value = np.ctypeslib.as_array(value)
        return value



class SharedBuf():
    '''
    Class to share arbitrary data buffers.
    Buffers are described with an MpStructure-derived class,
    which works like ctypes.Structure
    '''
    def __init__(self, desc):
        '''
        <desc> is a class or instance derived from MpStructure
        '''
        self._desc = desc
        self._size = ctypes.sizeof(desc)
        self._buf = multiprocessing.sharedctypes.RawArray(ctypes.c_char, self._size)
        self._cv = multiprocessing.Condition()

    def put( self, value):
        assert(self._size == ctypes.sizeof(value))
        try:
            self._cv.acquire()
            ctypes.memmove( self._buf, ctypes.pointer(value), self._size)
            self._cv.notify_all()   # Wake consumers up
            self._cv.release()
        except:
            # Always release lock. If we do not own it, we expect an AssertionError which can be ignored
            try:
                self._cv.release()
            except AssertionError:
                pass
            raise

    def get( self, next=True):
        try:
            # Only acquire the Condition object if we want to wait for the next frame.
            # There is no need to acquire it in other cases, since the data reading
            # is already properly locked by the underlying multiprocessing Array object.
            if next:
                self._cv.acquire()
                self._cv.wait()
            v = self._desc()
            ctypes.memmove( ctypes.pointer(v), self._buf, self._size)
            if next:
                self._cv.release()
            return v
        except:
            # Always release lock. If we do not own it, we expect an AssertionError which can be ignored
            try:
                self._cv.release()
            except AssertionError:
                pass
            raise


class SharedNumpyArray():
    '''
    numpy array implemented with a multiprocessing.Array shared object,
    plus a Condition to implement multi-consumer wait-for-next-frame semantics
    (similar to FLAO buflib).

    Usage from producer:

    frame = sharedNumpyArray( shape, dtype=np.float32)
    manager.register('frame', callable = lambda: frame)
    frame.put( value)  # This will wake up any consumer currently waiting on a get()

    Usage from consumers:

    manager.register('frame')
    f = manager.frame()
    value = f.get()   # Wait for next put() before returning
    value = f.get(next=False)  # Do not wait
    '''

    def __init__(self, shape, dtype=np.float32):
        n_elements = reduce(lambda x,y: x*y, shape)

        # Supported dtypes
        dt = {np.float32: ctypes.c_float, np.uint16: ctypes.c_ushort}

        self._cv = multiprocessing.Condition()
        try:
            self._array = multiprocessing.Array( dt[dtype], n_elements)
        except KeyError:
            print()
            print('Error: type '+str(dtype)+' is not supported')
            print()
            raise
        self._nparray = np.ctypeslib.as_array( self._array.get_obj())
        self._range = range(n_elements)
        self._shape = shape

    def put( self, value):
        try:
            self._cv.acquire()
            self._nparray.put( self._range, value)
            self._cv.notify_all()   # Wake consumers up
            self._cv.release()
        except:
            # Always release lock. If we do not own it, we expect an AssertionError which can be ignored
            try:
                self._cv.release()
            except AssertionError:
                pass
            raise

    def get( self, next=True):
        try:
            # Only acquire the Condition object if we want to wait for the next frame.
            # There is no need to acquire it in other cases, since the data reading
            # is already properly locked by the underlying multiprocessing Array object.
            if next:
                self._cv.acquire()
                self._cv.wait()
            v = self._nparray.take( self._range).reshape( self._shape)
            if next:
                self._cv.release()
            return v
        except:
            # Always release lock. If we do not own it, we expect an AssertionError which can be ignored
            try:
                self._cv.release()
            except AssertionError:
                pass
            raise

