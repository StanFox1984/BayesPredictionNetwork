#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from bayes_net import BayesNetwork, ObjectStringAssociator
from cgi import parse_qs
import os
import http.server
import socketserver

from http import HTTPStatus


PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
net = BayesNetwork(ObjectStringAssociator)

class Handler(http.server.SimpleHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		#print self.path
		s = self.path.replace("%20", " ")
		#print s
		s = s.replace("/", "")
		s = s.replace("?", "")
		#print s
		s = s.replace("'", "")
		#print s
		s = parse_qs(s)
		print str(s)
		if 'outcomes' in s:
			outcomes = s['outcomes'][0].split(',')
			s['outcomes'] = [ i.replace(" ", "") for i in outcomes ]
			print str(s)
                if 'submit' in s:
		    print "Learning outcomes: ", s['outcomes']
                    #self.wfile.write(str(s))
		    net.learn_outcomes(s['outcomes'])
		if 'predict' in s:
		    print "Predicting outcomes: ", s['outcomes'], s['steps']
		    o = net.predict_outcome(s['outcomes'][-1], int(s['steps'][0]))
		    print o
		    self.wfile.write(str(o))
                with open ("page.html", "r") as myfile:
			data=myfile.read()
		        self.wfile.write(data)
		return

try:
	#Create a web server and define the handler to manage the
	#incoming request
	port = int(os.getenv('PORT', 80))
	print('Listening on port %s' % (port))
	httpd = socketserver.TCPServer(('', port), Handler)
	httpd.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
