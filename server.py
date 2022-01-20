#!/usr/bin/python

#import sqlite3
import pickle

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from bayes_net import BayesNetwork, ObjectStringAssociator
from cgi import parse_qs

PORT_NUMBER = 8080

# This class will handle any incoming request from
# the browser
net = None

conn = None
ablob = None
net_id = -1


class myHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        global net_id
        global net
        global ablob
        global conn

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # Send the html message
        # print self.path
        s = self.path.replace("%20", " ")
        # print s
        s = s.replace("/", "")
        s = s.replace("?", "")
        # print s
        s = s.replace("'", "")
        # print s
        s = parse_qs(s)
        print(str(s))
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
            self.wfile.write(net.print_info_str())
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
        if "predict" in s:
            print("Predicting outcomes: ", s["outcomes"], s["steps"])
            o = net.predict_outcome(s["outcomes"][-1], int(s["steps"][0]))
            print(o)
            self.wfile.write(str(o))

        with open("page.html", "r") as myfile:
            data = myfile.read()
            self.wfile.write(data)
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
    myfile = open(str(net_id), "r")
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
    with open(str(net_id), "w") as myfile:
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
