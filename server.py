#!/usr/bin/python

#import sqlite3
import pickle

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from bayes_net import BayesNetwork, ObjectStringAssociator
from urllib.parse import parse_qs
from message_hub import message_hub
import os
import http.server
import socketserver

from io import BytesIO

PORT_NUMBER = 8080

# This class will handle any incoming request from
# the browser
net = None

conn = None
ablob = None
net_id = -1

def create_text_field_opening_tag(_id, name):
	s = '<textarea id="' + _id +'" name="' + name + '" rows="16" cols="150">'
	return s

def create_text_field_closing_tag():
	s = '</textarea>'
	return s

mbox = { }

hub = None

resync_freq = 1
resync_cnt = 0

class myHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_POST(self):
        global ablob
        global conn
        global mbox
        global resync_freq
        global resync_cnt
        global mbox_loaded
        global hub

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
#        response = BytesIO()
#        response.write(b'This is POST request. ')
#        response.write(b'Received: ')
#        response.write(body)
#        self.wfile.write(response.getvalue())

        if hub == None:
            create_or_open_db_from_file("mbox")
            ablob = load_blob_from_db_file("mbox", "mbox")
            if ablob != None:
                hub = pickle.loads(ablob[0])
            else:
                hub = message_hub()
        print (body)
        s = body.decode("utf-8")

        s = s.replace('\"', '')
        s = s.replace('\\', '')
        s = s.replace('/', '')
        s = s.replace('?', '')
        # print s
        s = s.replace('\'', '')
        s = parse_qs(s)

        print(str(s))
        data = hub.handle_request(s)
        self.wfile.write(data.encode())
        print ("mail box logic2")
        resync_cnt += 1
        if resync_cnt >= resync_freq:
            resync_cnt = 0
            d = pickle.dumps(hub)
            create_or_open_db_from_file("mbox")
            remove_blob_from_file("mbox", "mbox")
            insert_blob_to_file("mbox", d, "mbox")
            print ("Dumping message hub blob:")
            print (d)
    def do_PUT(self):
        global hub
        print ("Path: ", self.path)
        s = self.path.replace("%20", " ")
        # print s
        s = s.replace("/", "")
        s = s.replace("?", "")
        # print s
        s = s.replace("'", "")
        # print s
        s = parse_qs(s)
        print("Parsed path: ", str(s))
        path = s

        if hub == None:
            create_or_open_db_from_file("mbox")
            ablob = load_blob_from_db_file("mbox", "mbox")
            if ablob != None:
                hub = pickle.loads(ablob[0])
            else:
                hub = message_hub()

        if not hub.authenticate_as_admin(path):
            self.send_response(403)
            self.end_headers()
            return

        if "put_database" in path:
            if path.endswith('/'):
                self.send_response(405, "Method Not Allowed")
                self.wfile.write("PUT not allowed on a directory\n".encode())
                return
            else:
                try:
                    os.makedirs(os.path.dirname(path))
                except FileExistsError: pass
                length = int(self.headers['Content-Length'])
                with open("mbox", 'wb') as f:
                    f.write(self.rfile.read(length))
                self.send_response(201, "Created")
    def do_GET(self):
        global net_id
        global net
        global ablob
        global conn
        global mbox
        global resync_freq
        global resync_cnt
        global mbox_loaded
        global hub


        # Send the html message
        print ("Path: ", self.path)
        s = self.path.replace("%20", " ")
        # print s
        s = s.replace("/", "")
        s = s.replace("?", "")
        # print s
        s = s.replace("'", "")
        # print s
        s = parse_qs(s)
        print("Parsed path: ", str(s))

        if "mailbox" in s:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            if "id" in s and "message" in s:
                message = s["message"][0]
                _id = s["id"][0]
                if "send" in s:
                    mbox[_id] = message
                elif "recv" in s and _id in mbox:
                    self.wfile.write(mbox[_id].encode())
                    return
            with open("messagehub.html", "r") as myfile:
                data = myfile.read()
                self.wfile.write(data.encode())
            print ("mail box logic")
            return
        if "StanMessenger" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("stanmessenger.html", "r") as myfile:
                data = myfile.read()
                self.wfile.write(data.encode())
            return
        if "get_messenger.apk" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            with open("app-debug.apk", "rb") as myfile:
                data = myfile.read()
                self.wfile.write(data)
            return
        if "get_database.bin" in self.path:
            if hub == None:
                create_or_open_db_from_file("mbox")
                ablob = load_blob_from_db_file("mbox", "mbox")
                if ablob != None:
                    hub = pickle.loads(ablob[0])
                else:
                    hub = message_hub()
            if not hub.authenticate_as_admin(s):
                self.send_response(403)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            with open("mbox", "rb") as myfile:
                data = myfile.read()
                self.wfile.write(data)
            return
        if "mailbox_new" in s:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            if hub == None:
                    create_or_open_db_from_file("mbox")
                    ablob = load_blob_from_db_file("mbox", "mbox")
                    if ablob != None:
                        hub = pickle.loads(ablob[0])
                    else:
                        hub = message_hub()
            data = hub.handle_request(s)
            self.wfile.write(data.encode())
            print ("mail box logic2")
            resync_cnt += 1
            if resync_cnt >= resync_freq:
                resync_cnt = 0
                d = pickle.dumps(hub)
                create_or_open_db_from_file("mbox")
                remove_blob_from_file("mbox", "mbox")
                insert_blob_to_file("mbox", d, "mbox")
                print ("Dumping message hub blob:")
                print (d)
            return
        if "outcomes" in s:
            outcomes = s["outcomes"][0].split(",")
            s["outcomes"] = [i.replace(" ", "") for i in outcomes]
            print(str(s))
        if "Net id" in s and "load" in s:
            last_net_id = net_id
            net_id = int(s["Net id"][0])
            if last_net_id != net_id:
                ablob = load_blob_from_db_file("db", net_id)
                if ablob != None:
                    print("Loaded blob")
                    net = load_net_from_blob(ablob)
                else:
                    print("No blob found")
                    net = BayesNetwork(ObjectStringAssociator)
                last_net_id = net_id

            self.wfile.write(create_text_field_opening_tag("Bayes net", "Bayes net").encode())
            self.wfile.write(net.print_info_str().encode())
            self.wfile.write(create_text_field_closing_tag().encode())
        if "submit" in s:
            if net_id == -1:
                net_id = int(s["Net id"][0])
            print("Learning outcomes: ", s["outcomes"])
            # self.wfile.write(str(s))
            if net == None:
                net = BayesNetwork(ObjectStringAssociator)
            net.learn_outcomes(s["outcomes"])
            blob = pickle.dumps(net)
            if ablob != None:
                remove_blob_from_file("db", net_id)
            insert_blob_to_file("db", blob, net_id)
        if "predict" in s and "outcomes" in s:
            print("Predicting outcomes: ", s["outcomes"], s["steps"])
            o = net.predict_outcome(s["outcomes"][-1], int(s["steps"][0]))
            print(o)
            self.wfile.write(create_text_field_opening_tag("Results", "Results").encode())
            self.wfile.write(str(o).encode())
            self.wfile.write(create_text_field_closing_tag().encode())

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("page.html", "r") as myfile:
            data = myfile.read()
            self.wfile.write(data.encode())
        return


def create_or_open_db(db_file):
    db_is_new = not os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    if db_is_new:
        print("Creating schema")
        sql = """create table if not exists NETS(
        ID INTEGER,
        BAYES_NET BLOB)"""
        conn.execute(sql)  # shortcut for conn.cursor().execute(sql)
    else:
        print("Schema exists\n")
    return conn


def load_blob_from_db(db_file, net_id):
    conn = create_or_open_db(db_file)
    cur = conn.cursor()
    print(net_id)
    cur.execute("select * from NETS where ID=?", (net_id,))
    blob = cur.fetchone()
    cur.close()
    return blob

def load_net_from_blob(blob):
    net = pickle.loads(blob[1])
    net.print_info()
    return net

def create_or_open_db_from_file(db_file):
    if not os.path.exists(db_file):
        f = open(str(db_file), "w")
        f.close()
    return None

def load_blob_from_db_file(db_file, net_id):
    create_or_open_db_from_file(str(net_id))
    myfile = open(str(net_id), "rb")
    data = myfile.read()
    print(data)
    myfile.close()
    if len(data) == 0:
        print("Empty file!")
        return None
    return (data, data)

def remove_blob_from_file(db_file, net_id):
    os.remove(str(net_id)) 

def insert_blob_to_file(db_file, blob, net_id):
    with open(str(net_id), "wb") as myfile:
        myfile.write(blob)

try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(("", PORT_NUMBER), myHandler)
    print("Started httpserver on port ", PORT_NUMBER)

    # Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print("^C received, shutting down the web server")
    server.socket.close()
