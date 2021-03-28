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
                    self.queue[tag].cappend((ts, val))
                    print(self.queue[tag].cget())
                except Exception as e:
                    pass

class cdataset():
    def __str__(self):
        return "{}-{}, {}".format(self.start, self.end, str(self.data))

    def __repr__(self):
        return "{}-{}, {}".format(self.start, self.end, str(self.data))

    def __init__(self, capacity=10):
        self.start = 0
        self.end = 0
        self.capacity = capacity
        self.data = [None] * capacity

    def cappend(self, item):
        self.data[self.end] = item
        self.end += 1

        if self.end == self.capacity:
            self.end = 0

        if self.end - self.start <= 0:
            self.start += 1

        if self.start == self.capacity:
            self.start = 0

        #pp.pprint(self)

    def cget(self):
        if self.end < self.start:
            return self.data[self.start:self.capacity] + \
                   self.data[:self.end]

        return self.data[self.start:self.end]


sensorslist = {
    "vitesse"  : cdataset(),
    "altitude" : cdataset(),
    "gyro_x"   : cdataset(),
    "gyro_y"   : cdataset(),
    "gyro_z"   : cdataset(),
    "vide"     : cdataset(),
    "gps_lat"  : cdataset(),
    "gps_long" : cdataset()
}

app = Application(sensorslist)

while (True):
    if not app.client:
        app.wait()
    app.receive()
