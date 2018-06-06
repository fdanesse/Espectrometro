#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gc
import gtk
import gobject

gc.enable()

from gtk import gdk
from widgets import Visor
from Video.camara import Camara
from Processor.ImgProcessor import ImgProcessor

BASE_PATH = os.path.dirname(__file__)

gobject.threads_init()
gdk.threads_init()


class Main(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self)

        self.set_title("Espectrómetro")
        #self.set_icon_from_file(os.path.join(BASE_PATH,
        #    "Iconos", "..."))
        self.set_resizable(False)
        self.set_default_size(640, 480)
        self.set_border_width(4)
        self.set_position(gtk.WIN_POS_CENTER)

        self.processor = ImgProcessor()
        self.camara = False

        hbox = gtk.HBox()
        vbox = gtk.VBox()
        hbox.pack_start(vbox, True, True, 4)
        self.add(hbox)

        '''
        Descripcion de la interfaz
        ---------
        | 1 | 2 |
        | 3 | 4 |
        ---------
        1 - vista de la camara
        2 - fotografia a analizar
        3 - botones, play, stop, foto
        4 - datos del analisis
        '''

        # 1
        self.visor = Visor()
        self.visor.set_size_request(320, 240)
        vbox.pack_start(self.visor, True, True, 4)

        # 2
        vbox2 = gtk.VBox()
        self.image = gtk.Image()
        self.image.set_size_request(160, 120)
        self.image.modify_bg(0, gdk.Color(0, 0, 0))
        hbox.pack_start(vbox2, False, False, 0)
        vbox2.pack_start(self.image, False, False, 0)

        # 3
        hbox = gtk.HBox()
        self.btn_play = gtk.Button("PLAY")
        self.btn_play.modify_bg(0, gdk.Color(0, 0, 255))
        self.btn_stop = gtk.Button("STOP")
        self.btn_stop.modify_bg(0, gdk.Color(0, 0, 255))
        self.btn_foto = gtk.Button("FOTO")
        self.btn_foto.modify_bg(0, gdk.Color(0, 0, 255))

        hbox.pack_start(self.btn_play, False, False, 0)
        hbox.pack_start(self.btn_stop, False, False, 0)
        hbox.pack_end(self.btn_foto, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        # 4
        # ...

        self.connect("delete-event", self.__salir)
        self.visor.connect("realize", self.run)

        self.show_all()
        self.realize()

        print "process pid:", os.getpid()

    def run(self, event=False):
        xid = self.visor.get_property('window').xid
        self.camara = Camara(xid)
        self.btn_play.connect("clicked", self.camara.play)
        self.btn_stop.connect("clicked", self.camara.stop)
        self.btn_foto.connect("clicked", self.get_foto)
        self.camara.connect("update", self.update)

    def update(self, objeto, estado):
        if "PAUSED" in estado:
            self.btn_stop.set_sensitive(False)
            self.btn_foto.set_sensitive(False)
            self.btn_play.set_sensitive(True)
        elif "PLAYING" in estado:
            self.btn_stop.set_sensitive(True)
            self.btn_foto.set_sensitive(True)
            self.btn_play.set_sensitive(False)
        elif "NULL" in estado:
            self.btn_stop.set_sensitive(False)
            self.btn_foto.set_sensitive(False)
            self.btn_play.set_sensitive(True)
            self.visor.modify_bg(0, gdk.Color(0, 0, 0))
        #else:
        #    print objeto, estado

    def get_foto(self, button=False):
        pixbuf = self.camara.foto()
        pixbuf = self.processor.scale_full(self.image, pixbuf)
        self.image.set_from_pixbuf(pixbuf)
        gobject.idle_add(self.__procesar, pixbuf)

    def __procesar(self, pixbuf):
        array = self.processor.getColorPromedio(pixbuf)

    def __salir(self, widget=None, senial=None):
        gtk.main_quit()
        sys.exit(0)


if __name__ == "__main__":
    Main()
    gtk.main()
