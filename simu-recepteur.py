#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
from random import random
from time import sleep

FREQ=.1

class Recepteur:
    def __init__(self, port=8889):
        self.clientAddress   = 0
        self.client = 0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print("Listening on port:{}".format(port))
        self.server.listen()

    def send(self, msg, tag="NULL", timestamp="00000000"):
        if self.client:
            print("Sending message: "+ msg)
            rawmsg = timestamp + " " + tag + ": " + msg + "\n"
            self.client.sendall(rawmsg.encode())

    def wait(self):
        print("Waiting for new connections: ")
        self.client, self.clientAddress = self.server.accept()
        print("Accepted a connection request from {}:{}"
              .format(self.clientAddress[0], self.clientAddress[1]))


class Capteur:
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

# ---- Capteurs de test ------
capteurs = {
    "vitesse"  : Capteur("vitesse", 0.3),
    "altitude" : Capteur("Altitude", 0.1),
    "gyro_x"   : Capteur("Inclinaison_x", 0.6),
    "gyro_y"   : Capteur("Inclinaison_y", 0.6),
    "gyro_z"   : Capteur("Inclinaison_z", 0.6),
    "gps_lat"  : Capteur("GPS_lat", 1),
    "gps_long" : Capteur("GPS_long", 1),
    "vide"     : Capteur("vide", 1),
}
# ---- Capteurs de test ------
recepteur = Recepteur()
while (True):
    if not recepteur.client:
        recepteur.wait()
    for name, capteur in capteurs.items():
        recepteur.send(str(capteur.data), tag=name)
    sleep(FREQ)
