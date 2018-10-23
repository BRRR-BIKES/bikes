#!/usr/bin/env python3
"""
Very simple HTTP server in python.

Usage::
    ./dummy-web-server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""
import os
import time
from cgi import parse_header, parse_multipart
from sys import version as python_version
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

database = {
            'time':[str(time.time())],
            'longtitude':['0.0'],
            'latitude':['0.0'],
            'theft':['0']
            }

if python_version.startswith('3'):
    from urllib.parse import parse_qs
    from http.server import BaseHTTPRequestHandler
else:
    from urlparse import parse_qs
    from BaseHTTPServer import BaseHTTPRequestHandler

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        global database

        # Retrieve last location and theft status
        # This method supposed to be called by android app
        if (self.path == '/get') or (self.path == '/get/'):
            lat = [e for e in database['latitude'] if e != ''][-1]
            lon = [e for e in database['longtitude'] if e != ''][-1]
            theft = database['theft'][-1]
            self.wfile.write(str(lat)+'\n'+str(lon) + '\n' + str(theft)+'\n')

        # This method supposed to be called by tacker within the bike
        if self.path[0:5] == '/set/':
            string_to_parse = self.path[5:]
            getvars = parse_qs(
                    string_to_parse,
                    keep_blank_values=1)
            # save data as bunch of strings
            database['time'].append(str(time.time()))
            if 'long' in getvars.keys():
                database['longtitude'].append(getvars['long'][0])
            else:
                database['longtitude'].append('')

            if 'lat' in getvars.keys():
                database['latitude'].append(getvars['lat'][0])
            else:
                database['latitude'].append('')

            if 'theft' in getvars.keys():
                database['theft'].append(getvars['theft'][0])
            else:
                database['theft'].append('')

    # do nothing
    def do_HEAD(self):
        self._set_headers()

    # useless now, nobody call this function
    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif (ctype == 'application/x-www-form-urlencoded') or (ctype == 'application/json'):
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                    self.rfile.read(length),
                    keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    # do nothing
    def do_POST(self):
        self._set_headers()

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    # PORT is set withing heroku's enviroment variable to 80
    port = int(os.environ.get('PORT', 5000))
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run(port=port)

