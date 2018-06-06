#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import pygst
import gst
import gtk


class Camara(gobject.GObject):

    __gsignals__ = {
    "update": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,))}

    def __init__(self, ventana_id, device="/dev/video1"):

        gobject.GObject.__init__(self)

        self.estado = None
        self.ventana_id = ventana_id
        self.pipeline = gst.Pipeline()

        # Camara
        camara = v4l2src_bin()
        camara.set_device(device)
        self.pipeline.add(camara)

        # MultiPlexor
        tee = gst.element_factory_make('tee', "tee")
        tee.set_property('pull-mode', 1)
        self.pipeline.add(tee)

        # Pantalla
        xvimage = xvimage_bin()
        self.pipeline.add(xvimage)

        # Imagenes
        fotobin = Foto_bin()
        self.pipeline.add(fotobin)

        camara.link(tee)
        tee.link(xvimage)
        tee.link(fotobin)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_mensaje)
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message', self.__sync_message)

        self.play()

    def __sync_message(self, bus, message):
        if message.type == gst.MESSAGE_ELEMENT:
            if message.structure.get_name() == 'prepare-xwindow-id':
                gtk.gdk.threads_enter()
                gtk.gdk.display_get_default().sync()
                message.src.set_xwindow_id(self.ventana_id)
                gtk.gdk.threads_leave()
        elif message.type == gst.MESSAGE_ERROR:
            print "ERROR:", message.parse_error()
        elif message.type == gst.MESSAGE_STATE_CHANGED:
            old, new, pending = message.parse_state_changed()
            if self.estado != new:
                self.estado = new
                self.emit("update", str(self.estado))

    def __on_mensaje(self, bus, message):
        if message.type == gst.MESSAGE_ERROR:
            print "ERROR:", message.parse_error()

    def play(self, button=False):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def stop(self, button=False):
        self.pipeline.set_state(gst.STATE_NULL)

    def foto(self, button=False):
        gdkpixbufsink = self.pipeline.get_by_name("gdkpixbufsink")
        pixbuf = gdkpixbufsink.get_property('last-pixbuf')
        return pixbuf


class v4l2src_bin(gst.Bin):
    """
    Bin de entrada de camara v4l2src.
    """

    def __init__(self):

        gst.Bin.__init__(self)

        self.set_name('jamedia_camara_bin')

        camara = gst.element_factory_make("v4l2src", "v4l2src")

        caps = gst.Caps('video/x-raw-yuv,framerate=30/1')
        camerafilter = gst.element_factory_make("capsfilter", "camera_filter")
        camerafilter.set_property("caps", caps)

        self.add(camara)
        self.add(camerafilter)

        camara.link(camerafilter)

        self.add_pad(gst.GhostPad("src", camerafilter.get_static_pad("src")))

    def set_device(self, device):
        camara = self.get_by_name("v4l2src")
        camara.set_property("device", device)


class xvimage_bin(gst.Bin):
    """
    Salida de video a pantalla.
    """

    def __init__(self):

        gst.Bin.__init__(self)

        self.set_name('xvimage_bin')

        queue = gst.element_factory_make('queue', "queue")
        queue.set_property("max-size-buffers", 1000)
        queue.set_property("max-size-bytes", 0)
        queue.set_property("max-size-time", 0)

        ffmpegcolorspace = gst.element_factory_make(
            'ffmpegcolorspace', "ffmpegcolorspace")
        videorate = gst.element_factory_make('videorate', "videorate")

        xvimagesink = gst.element_factory_make('xvimagesink', "xvimagesink")
        xvimagesink.set_property("force-aspect-ratio", True)
        xvimagesink.set_property("synchronous", False)

        try:
            videorate.set_property("max-rate", 30)
        except:
            pass

        self.add(queue)
        self.add(ffmpegcolorspace)
        self.add(videorate)
        self.add(xvimagesink)

        queue.link(ffmpegcolorspace)
        ffmpegcolorspace.link(videorate)
        videorate.link(xvimagesink)

        self.add_pad(gst.GhostPad("sink", queue.get_static_pad("sink")))


class Foto_bin(gst.Bin):

    def __init__(self):

        gst.Bin.__init__(self)

        self.set_name('Foto_bin')

        queue = gst.element_factory_make("queue", "queue")
        queue.set_property("leaky", 1)
        queue.set_property("max-size-buffers", 1)

        ffmpegcolorspace = gst.element_factory_make(
            "ffmpegcolorspace", "ffmpegcolorspace")
        videorate = gst.element_factory_make('videorate', "videorate")
        gdkpixbufsink = gst.element_factory_make(
            "gdkpixbufsink", "gdkpixbufsink")
        gdkpixbufsink.set_property("post-messages", False)

        try:
            videorate.set_property("max-rate", 30)
        except:
            pass

        self.add(queue)
        self.add(ffmpegcolorspace)
        self.add(videorate)
        self.add(gdkpixbufsink)

        queue.link(ffmpegcolorspace)
        ffmpegcolorspace.link(videorate)
        videorate.link(gdkpixbufsink)

        self.add_pad(gst.GhostPad("sink", queue.get_static_pad("sink")))
