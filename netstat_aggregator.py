#!/usr/bin/python

import sys
import json
import bsddb
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

data = bsddb.btopen('netstat_aggregated.db', 'c')

class AggregatorRequestHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		try:
			length = int(self.headers.getheader('content-length'))
			contentdata = self.rfile.read(length)

			jsondata = json.loads(contentdata)

			for (canonical_conn,count) in jsondata.items():
				canonical_conn = str(canonical_conn)
				if canonical_conn not in data:
					data[canonical_conn]='0'

				data[canonical_conn]=str(int(data[canonical_conn]) + 1)

			print data

			self.send_response(200)
		except:
			self.send_response(400)


if sys.argv[1:]:
    listen_ip = sys.argv[1]
else:
    listen_ip = '0.0.0.0'

if sys.argv[2:]:
    port = int(sys.argv[2])
else:
    port = 9587


server_address = (listen_ip, port)

httpd = HTTPServer(server_address, AggregatorRequestHandler)

sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()

