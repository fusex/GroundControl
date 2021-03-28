#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import random
from kivy.core.text import Label as CoreLabel
from kivy.config import Config
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.properties import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
import serial

# fréquence d'acquisition de signal
from SpaceX_widget import SpaceXWidget, ControleTir

FREQ = .1


class Recepteur:
    """Capteur alimenté par la liaison série"""
    def __init__(self, nom=""):
        try:
            self.ser = serial.Serial('/dev/cu.usbmodem1411', 9600)
        except:
            print("no reception")
        self.nom = nom
        self.data = .0
        Clock.schedule_interval(self.recepteur_update, FREQ)

    def recepteur_update(self, dt):
        try:
            value = float(self.ser.readline().strip())
            print(value/1000)
            if value/1000 < 10:
                self.data = value/1000
        except:
            self.data = 0


class CapteurTest:
    """Classe de dévelopement de l'application
    A remplacer plus tard par l'acquisition des signaux réels du port série"""
    def __init__(self, nom="", coef=1.):
        self.nom = nom
        self.data = .0
        self.coef = coef
        #self.rand = 0
        Clock.schedule_interval(self.capteur_update, FREQ)

    def capteur_update(self, dt):
        if self.nom == "Altitude":
            self.data = self.data + random() * 2
        else:
            self.data = self.coef * (random() * 200 - 50) + 50

    def capteur_update2(self, dt):
        self.rand += 1
        if self.nom == "Altitude":
            self.data = self.data + self.rand * 2
        else:
            self.data = self.coef * (self.rand * 200 - 50) + 50
        # print(self.nom + " : " + str(self.data))


# ---- Capteurs de test ------
vitesse = CapteurTest("vitesse", 0.3)
altitude = CapteurTest("Altitude", 0.1)
gyro_x = CapteurTest("Inclinaison_x", 0.6)
gyro_y = CapteurTest("Inclinaison_y", 0.6)
gyro_z = CapteurTest("Inclinaison_z", 0.6)
gps_lat = CapteurTest("GPS_lat", 1)
gps_long = CapteurTest("GPS_long", 1)
vide = CapteurTest("vide", 0)
reception = Recepteur()
# ---- Capteurs de test ------

def crange(start, length):
    rang = list(range(start, length))
    if start > 0:
        rang += list(range(0, length - start))
    return  rang

def lastelement(start, length):
    if start == 0:
        return length-1
    return start-1


class Graphique(RelativeLayout):
    courbe = []

    def __init__(self, capteur, titre="", **kvargs):
        super().__init__(**kvargs)
        self.g = []
        self.titre = titre
        self.L = 300
        self.H = 200
        self.start = 0
        self.graphX = []
        self.graphY = []
        self.y_mid = self.H / 2
        self.capteur = capteur
        self.label_titre = Label(text=self.titre,
                                 color=(1, 0.5, 0),
                                 text_size=(self.width, self.height),
                                 size_hint=(1, 2),
                                 padding_y=0)
        self.add_widget(self.label_titre)
        Clock.schedule_interval(self.update, FREQ)
        self.temps = 0
        pas = int(300/10*FREQ)
        # pas = 3
        max_graph = int(10/FREQ)
        self.tail = max_graph -1
        if self.capteur.nom == "Altitude":
            for i in range(0, max_graph):
                self.graphX.append(pas*i)
                self.graphY.append(0)
        else:
            for i in range(0, max_graph):
                self.graphX.append(pas*i)
                # pas*i = 89*3 =
                self.graphY.append(self.y_mid)

        self.container_layout = BoxLayout(opacity=0.5)

        with self.container_layout.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.add_widget(self.label_titre)
        self.chart_unit()

        self.add_widget(self.container_layout)

    def update(self, dt):
        self.temps += FREQ

    def update0(self, dt):
        self.temps += FREQ
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        pas = int(300/10*FREQ)
        max_graph = int(10 / FREQ)

        lastx = self.x
        self.x += 0
        with self.canvas:
            Color(0, 1, 1)
            Line(points=(lastx, 100, self.x, 100))

    def update0(self, dt):
        self.temps += FREQ
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        pas = int(300/10*FREQ)
        max_graph = int(10 / FREQ)

        lastx = 0
        lasty = self.graphY[self.start]
        self.start -= 1
        if self.start == -1:
            self.start = max_graph -1

        for i in crange(self.start, max_graph):
            y = self.graphY[i]
            x = lastx + pas
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(lastx, lasty, x, y))
            lastx = x
            lasty = y

    def update1(self, dt):
        self.temps += FREQ
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        pas = int(300/10*FREQ)
        max_graph = int(10 / FREQ)

        #print("max:"+str(max_graph))
        #self.graphY[lastelement(self.start, max_graph)] = self.capteur.data
        self.graphY[self.tail] = self.capteur.data
        x = (max_graph+1)*pas
        lasty = -1
        #x = 0
        for i in crange(self.start, max_graph):
            y = self.graphY[i]
            x -= pas
            if lasty != -1:
                with self.canvas:
                    Color(0, 1, 1)
                    Line(points=(lastx, lasty, x, y))
            lastx = x
            lasty = y

        self.start -= 1
        if self.start == -1:
            self.start = max_graph -1

        self.tail += 1
        if self.tail == max_graph:
            self.tail = 0

        print("X:%d, start:%d, max_graph:%d, tail:%d".format(x,self.start,max_graph,self.tail))

    def update2(self, dt):
        self.temps += FREQ
        self.canvas.clear()
        # Dessin du cadre
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        # Trace la courbe
        pas = int(300/10*FREQ)
        max_graph = int(10 / FREQ)
        for i in range(0, max_graph-1):
            x1 = self.graphX[i]
            y1 = self.graphY[i]
            x2 = self.graphX[i + 1]
            y2 = self.graphY[i + 1]
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(x1, y1, x2, y2))
        # mise à jour des points avec intégration de la nouvelle valeur
        # à la fin
        for i in range(0, max_graph-1):
            self.graphY[i] = self.graphY[i + 1]
        # Mise à jour de de la valeur du capteur
        self.graphY[max_graph-1] = self.capteur.data

    def chart_unit(self):
        for i in range(0,10):
            mylabel = CoreLabel(text=str(i-9), font_size=15, color=(1, 1, 1, 1))
            # Force refresh to compute things and generate the texture
            mylabel.refresh()
            # Get the texture and the texture size
            texture = mylabel.texture
            texture_size = list(texture.size)
            self.g.append(Rectangle(pos=(17+i*30, 100), texture=texture, size=texture_size))
            with self.container_layout.canvas:
                Line(points=(30+i*30, 100, 30+i*30, 105))
            # Draw the texture on any widget canvas
            self.container_layout.canvas.add(self.g[i])


class MainWidget(BoxLayout):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        pass


class GroundControlStationApp(App):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)

    def build(self):
        self.title = 'Ground Control Station - Section Espace'
        box = BoxLayout(orientation="vertical")
        layout = GridLayout(cols=3)

        my_controle_tir = ControleTir()
        layout.add_widget(my_controle_tir)
        layout.add_widget(Graphique(vitesse, "Vitesse"))
        #layout.add_widget(Graphique(altitude, "Altitude"))
        #layout.add_widget(Graphique(gyro_x, "inclinaison_x"))
        #layout.add_widget(Graphique(gyro_y, "inclinaison_y"))
        #layout.add_widget(Graphique(gyro_z, "inclinaison_z"))
        #layout.add_widget(Graphique(gps_lat, "GPS_L"))
        #layout.add_widget(Graphique(gps_long, "GPS_l"))
        #layout.add_widget(Graphique(reception, "Recepteur"))
        box.add_widget(layout)
        #box.add_widget(SpaceXWidget(my_controle_tir))
        #box.add_widget(layout)

        return box


Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

GroundControlStationApp().run()
