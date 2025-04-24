# -*- coding: utf-8 -*-
"""
@author: Mihai Pruna
use at own risk, no warranty implied or provided
"""
#!/usr/bin/env python3

#entry file, starts server
import time
from http.server import HTTPServer
from myserver import FServer
#run locally
HOST_NAME = 'localhost'
PORT_NUMBER = 8000

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), FServer)
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))