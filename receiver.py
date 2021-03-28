#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, errno, time
from time import sleep
import pprint

pp = pprint.PrettyPrinter(indent=4)

class Application():
    def __init__(self, queue, port=8889):
        self.client = 0
        self.queue = queue

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print("Listening on port:{}".format(port))
        self.server.listen()

    def wait(self):
        print("Waiting for new connections: ")
        self.client, address = self.server.accept()
        print("Accepted a connection request from {}:{}"
              .format(address[0], address[1]))

    def receive(self):
        try:
            data = self.client.recv(1024)
        except Exception as e:
            error = True

        if not data:
            print("Disconnected")
            self.client.close()
            self.client = 0
            return

        self.push(data.decode())

    def push(self, data):
        for msg in data.split('\n'):
            if msg:
                #print(msg + "=>" + str(len(msg)))
                tokens = msg.split(' ')
                try:
                    ts  = tokens[0]
                    tag = tokens[1][:-1]
                    val = tokens[2][:-1]
                    self.cappend(tag, (ts, val))
                except Exception as e:
                    pass

    def cappend(self, sensor_name, item):
        try:
            self.queue[sensor_name] += {item}
            pp.pprint(self.queue)
        except Exception as e:
            pass

sensorslist = {
    "vitesse"  : [],
    "altitude" : [],
    "gyro_x"   : [],
    "gyro_y"   : [],
    "gyro_z"   : [],
    "vide"     : [],
    "gps_lat"  : [],
    "gps_long" : []
}

app = Application(sensorslist)

while (True):
    if not app.client:
        app.wait()
    app.receive()
