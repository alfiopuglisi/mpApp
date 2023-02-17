#!/usr/bin/env python

# Example client

from mpApp.mpManager import createClientManager

class MpClient:

    def __init__(self, mpConfig):
        self.manager = createClientManager(mpConfig.HOST,
                                           mpConfig.PORT,
                                           mpConfig.AUTHKEY,
                                           mpConfig.data,
                                           mpConfig.modules.keys())

    def send(self, dest, msg):
        outpipe = getattr(self.manager, '%s_out' % dest).__call__()
        outpipe.send(msg)


class _ExampleClient(MpClient):

    def __init__(self, mpConfig):
        super().__init__(mpConfig)

        self.pxdata = self.manager.pixels()
        self.rtc = self.manager.rtc()

    def pixels(self):
        return self.pxdata.get(True)

    def rtcdata(self):
        return self.rtc.get(True)


if __name__ == '__main__':
    # speedtest

    client = _ExampleClient()
    while True:
        data = client.rtcdata()
        print(data.fcounter)
        print(data.calibpixels)
