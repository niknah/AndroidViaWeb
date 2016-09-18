# pylint: disable=invalid-name,missing-docstring,super-on-old-class,bad-continuation,too-many-return-statements

import sys
import argparse
import StringIO
import re
import os
import time
import urllib
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
homeDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(homeDir+'/AndroidViewClient/src')

from com.dtmilano.android.viewclient import ViewClient



class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    #Handler for the GET requests
    def defaultHeader(self, contentType):
        self.send_response(200)
        self.send_header('Content-type', contentType)
        self.end_headers()


    def do_GET(self):
        attempt = 0
        while attempt < 3:
            attempt += 5
            try:
                self.do_GET2()
            except Exception,e:
                print 'error:'+str(e)
                print 'error0:'+str(e.args[0])
                print("reconnect, wait...")
                time.sleep(5)
                self.main.connect()
                print("reconnected...")

    def do_GET2(self):
        self.main = self.server.androidViaWeb
        if self.path == '/':
            self.defaultHeader('text/html')
            # Send the html message
            f = open(homeDir+"/index.html")
            self.wfile.write(f.read())
            f.close()
            return
        screenshotM = self.main.screenshotRe.match(self.path)
        if screenshotM is not None:
            q = urlparse.parse_qs(screenshotM.group(1))
            imageFormat = q['imageFormat'][0]
            img = self.main.screenshotPng(q['r'][0], imageFormat)
            self.defaultHeader('image/'+imageFormat)
            self.wfile.write(img)
            return

        typeM = self.main.typeRe.match(self.path)
        clickM = self.main.clickRe.match(self.path)
        if clickM is None and typeM is None:
            self.send_response(404)
            self.wfile.write("404 You are lost")
            return
        if clickM is not None:
            if clickM.group(1) == 'touch':
                self.defaultHeader('application/json')
                self.main.touch(clickM.group(2).split(','))
                self.wfile.write('{"ok":true}')
                return
            elif clickM.group(1) == 'swipe':
                self.defaultHeader('application/json')
                self.main.swipe(clickM.group(2).split(','))
                self.wfile.write('{"ok":true}')
                return
        elif typeM is not None:

            typeStr = urllib.unquote(typeM.group(2))
            if typeM.group(1) == 'type':
                self.defaultHeader('application/json')
                self.main.device.type(typeStr)
                self.wfile.write('{"ok":true}')
                return
            elif typeM.group(1) == 'press':
                self.defaultHeader('application/json')
                self.main.device.press(typeStr)
                self.wfile.write('{"ok":true}')
                return



class AndroidViaWeb(object):
    def __init__(self):
        self.port = 8080
        self.serial = None
        self.serialno = None
        self.device = None
        self.typeRe = re.compile(r'^/(press|type)\?k=(\S+)$')
        self.clickRe = re.compile(r'^/(touch|swipe)\?l=([0-9,]+)$')
        self.screenshotRe = re.compile(r'^/screenshot.png\?(.+)$')

    def connect(self):
        (self.device, self.serialno) = ViewClient.connectToDeviceOrExit(serialno=self.serial,ignoreversioncheck=True)

    def start(self):
        self.parseArgs()
        self.connect()
        self.serveWeb()

    def touch(self, arr):
        self.device.longTouch(int(arr[0]), int(arr[1]), int(arr[2]))

    def swipe(self, arr):
        self.device.drag(
            (int(arr[0]), int(arr[1])),
            (int(arr[2]), int(arr[3])),
            int(arr[4])
            )

    def screenshotPng(self, rotate, imageFormat):
        # *** Bad: on some devices, this is compressing in png then uncompressing to PIL, then re-compressing again.
        image = self.device.takeSnapshot()
        rotate = int(rotate)
        transpose = None
        if rotate == 90:
            transpose = Image.ROTATE_90
        elif rotate == 180:
            transpose = Image.ROTATE_180
        elif rotate == 270:
            transpose = Image.ROTATE_270
        if transpose is not None:
            image = image.transpose(transpose)
        output = StringIO.StringIO()
        image.save(output, imageFormat)
        contents = output.getvalue()
        output.close()
        return contents

    def parseArgs(self):
        parser = argparse.ArgumentParser(description='Android')
        parser.add_argument('--port', dest='port',
            action='store', help='Port number')
        parser.add_argument('--serial', dest='serial',
            action='store', help='Serial number')
        args = parser.parse_args()
        if args.port:
            self.port = int(args.port)
        if args.serial:
            self.serial = args.serial

    def serveWeb(self):
        try:
            #Create a web server and define the handler to manage the
            #incoming request
            server = HTTPServer(('', self.port), MyHandler)
            server.androidViaWeb = self
            print 'Started httpserver on port ', self.port

            #Wait forever for incoming htto requests
            server.serve_forever()

        except KeyboardInterrupt:
            print '^C received, shutting down the web server'
            server.socket.close()


androidViaWeb = AndroidViaWeb()
androidViaWeb.start()

# vim: set smartindent expandtab ts=4 sw=4:
