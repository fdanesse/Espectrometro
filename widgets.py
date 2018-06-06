#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
from gtk import gdk

class Visor(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.modify_bg(0, gdk.Color(0, 0, 0))
        self.show_all()
