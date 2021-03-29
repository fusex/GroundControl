#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, errno, time
from random import random
from time import sleep
import threading

FREQ=.1

class DataForwarder:
    def __init__(self, host="127.0.0.1", port=8889):
        self.connected = False
        self.host = host
        self.port = port

    def send(self, msg, tag="NULL", timestamp=0):
        if self.connected:
            rawmsg = "{:.4f} {}: {}\n".format(timestamp, tag, msg)
            print("Sending message: "+ rawmsg, end = '')
            try:
                self.conn.sendall(rawmsg.encode())
            except Exception as e:
                self.connected = False

    def wait(self):
        print("Connecting to host:{} and port:{}"
              .format(self.host, self.port))
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.host, self.port))
            self.connected = True
        except Exception as e:
            self.conn.close()
            self.connected = False

class Sensor:
    def __init__(self, nom="", coef=1.):
        self.nom = nom
        self.idata = .0
        self.coef = coef

    @property
    def data(self):
        if self.nom == "Altitude":
            self.idata += random() * 2
        else:
            self.idata = self.coef * (random() * 200 - 50) + 50

        return self.idata

sensors = {
    "vitesse"  : Sensor("vitesse", 0.3),
    "altitude" : Sensor("Altitude", 0.1),
    "gyro_x"   : Sensor("Inclinaison_x", 0.6),
    "gyro_y"   : Sensor("Inclinaison_y", 0.6),
    "gyro_z"   : Sensor("Inclinaison_z", 0.6),
    "gps_lat"  : Sensor("GPS_lat", 1),
    "gps_long" : Sensor("GPS_long", 1),
    "vide"     : Sensor("vide", 1),
}

def gettimestamp():
    return time.time() - t0

def main():
    threading.Timer(FREQ, main).start()
    if not forwarder.connected:
        forwarder.wait()
    for name, sensor in sensors.items():
        forwarder.send('{:.4f}'.format(sensor.data), name, gettimestamp())

t0 = time.time()
forwarder = DataForwarder()
main()
