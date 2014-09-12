#!/usr/bin/python

import sys
import json
import bsddb
import ipaddress
import binascii
import networkx as nx
import matplotlib.pyplot as plt
import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

STATE = {
        '01':'ESTABLISHED',
        '02':'SYN_SENT',
        '03':'SYN_RECV',
        '04':'FIN_WAIT1',
        '05':'FIN_WAIT2',
        '06':'TIME_WAIT',
        '07':'CLOSE',
        '08':'CLOSE_WAIT',
        '09':'LAST_ACK',
        '0A':'LISTEN',
        '0B':'CLOSING'
        }


data = bsddb.btopen('netstat_aggregated.db', 'c')
G=nx.Graph()
nodesize=1000

class UIRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			self.send_response(200)
			self.send_header('Content-type', 'image/png')
			self.end_headers()

			html = ''
			html += '<html><head><title>titulo</title></head><h1>dados</h1>'
			for (canonical_conn,count) in data.items():
				ip1, ip2, state = str(canonical_conn).split('_')
			
				ip1 = ipaddress.IPv4Address(binascii.unhexlify(ip1)) if len(ip1) <= 8 else ipaddress.IPv6Address(binascii.unhexlify(ip1))
				ip2 = ipaddress.IPv4Address(binascii.unhexlify(ip2)) if len(ip2) <= 8 else ipaddress.IPv6Address(binascii.unhexlify(ip2))

				G.add_edge(ip1, ip2, weight=count)

			edgewidth=[]
			for (u,v,d) in G.edges(data=True):
				edgewidth.append(G.get_edge_data(u,v)['weight'])

			pos=nx.graphviz_layout(G)
			nx.draw_networkx_edges(G,pos,alpha=0.3,width=edgewidth, edge_color='m')
			nx.draw_networkx_nodes(G,pos,node_size=nodesize,node_color='w',alpha=0.4)
			nx.draw_networkx_edges(G,pos,alpha=0.4,node_size=0,width=1,edge_color='k')
			nx.draw_networkx_labels(G,pos,fontsize=14)

			imgdata = StringIO.StringIO()
			plt.savefig(imgdata)
			imgdata.seek(0)

			self.wfile.write(imgdata.buf)
		except:
			print sys.exc_info()[0]
			self.send_response(400)


if sys.argv[1:]:
    listen_ip = sys.argv[1]
else:
    listen_ip = '0.0.0.0'

if sys.argv[2:]:
    port = int(sys.argv[2])
else:
    port = 8080


server_address = (listen_ip, port)

httpd = HTTPServer(server_address, UIRequestHandler)

sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()

