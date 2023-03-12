#!/usr/bin/env python

class MpConfig():

    def __init__(self, PORT, AUTHKEY, data, modules, HOST='localhost'):
        self.HOST = HOST
        self.PORT = PORT
        self.AUTHKEY = AUTHKEY
        self.data = data
        self.modules = modules


# ___oOo___
