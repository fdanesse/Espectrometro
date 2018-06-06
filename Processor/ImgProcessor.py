#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import gtk
import numpy

class ImgProcessor(gobject.GObject):

    def __init__(self):

        gobject.GObject.__init__(self)

    def scale_full(self, widget, pixbuf):
        """
        Escala ocupando todo el espacio visible del widget donde debe dibujarse
        pero sin perder proporciones de la imagen.
        """
        rect = widget.get_allocation()
        try:
            src_width, src_height = pixbuf.get_width(), pixbuf.get_height()
            scale = min(float(rect.width) / src_width,
                float(rect.height) / src_height)
            new_width = int(scale * src_width)
            new_height = int(scale * src_height)
            pixbuf = pixbuf.scale_simple(new_width,
                new_height, gtk.gdk.INTERP_BILINEAR)
            return pixbuf
        except:
            return None

    def getColorPromedio(self, pixbuf):
        array = pixbuf.get_pixels_array()
        pixels = numpy.copy(array)
        s = pixels.shape
        print "Datos Listos para ser Procesados. Tamaño del Array:", s, "=", s[0] * s[1] * s[2], "bytes"
        return pixels
