#!/usr/bin/env python

# Example client

import mpManager

class Client:

    def __init__(self, mpConfig):
        manager = MpManager.createClientManager('localhost', mpConfig.PORT, mpConfig.AUTHKEY, mpConfig.data)
        self.pxdata = manager.pixels()
        self.rtc = manager.rtc()

    def pixels(self):
        return self.pxdata.get(True)

    def rtcdata(self):
        return self.rtc.get(True)


if __name__ == '__main__':
    # speedtest

    client = Client()
    while True:
        data = client.rtcdata()
        print(data.fcounter)
        print(data.calibpixels)
