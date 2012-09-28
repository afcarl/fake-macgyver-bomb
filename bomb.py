import threading

import time
import serial
import pygame

from gi.repository import Gtk, Gdk, GObject

GObject.threads_init()
Gdk.threads_init()
pygame.init()

class Clock(Gtk.EventBox):
    def __init__(self, size=100):
        Gtk.EventBox.__init__(self)

        self._size = size

        bg = Gdk.RGBA()
        bg.parse('black')
        self.override_background_color(Gtk.StateFlags.NORMAL,bg)

        self._l = Gtk.Label()
        fg = Gdk.RGBA()
        fg.parse("white")
        self._l.override_color(Gtk.StateFlags.NORMAL,fg)
        self.add(self._l)

    def set_time(self, timestr):
        self._l.set_markup('<span font="DS-Digital %d">%s</span>' % (self._size,timestr))
        #return false for idle_add
        return False

class SerialThread(threading.Thread):
    def __init__(self, port, cb):
        threading.Thread.__init__(self, name="ardunio-thread")
        self._cb = cb
        self.daemon = True

        self._ser = serial.Serial(port, 9600, timeout=1)
        self._ser.open()

        assert self._ser.isOpen()

    def run(self):
        while 1:
            val = self._ser.readline()
            try:
                self._cb(int(val) if val else 0)
            except:
                pass
        self._ser.close()

class Bomb:
    def __init__(self, port='/dev/ttyACM0', adc_min=0, adc_max=1024, 
                        time_start="23:59:59", time_steps=66):
        self._w = Gtk.Window()
        self._w.connect("delete-event", self.quit)
        self._clock = Clock()
        self._w.add(self._clock)
        self._thread = SerialThread(port, self._got_data)

        self._start = time.mktime(time.strptime(time_start,"%H:%M:%S"))
        self._boom = time.mktime(time.strptime("00:00:00", "%H:%M:%S"))
        self._steps = int(time_steps)
        self._tstep = int(self._start - self._boom)/self._steps
        self._RMIN = int(adc_min)
        self._RMAX = int(adc_max)
        self._oldval = 0

        self._thread.start()

    def _scale_val(self, val):
        N = self._steps
        X0 = self._RMIN
        X1 = self._RMAX
        val = min(max(val, X0), X1)
        return int(1.*N*(val - X0)/(X1 - X0))

    def _got_data(self, val):
        #timestr = "00:00:%d" % val #strftime
        v = self._scale_val(val)
        if self._oldval != v:
            self._oldval = v
            pygame.mixer.Sound('tos-redalert.wav').play()

        t = time.localtime(max( (self._start - v * self._tstep
                                 - time.time()%self._tstep ), self._boom))
        timestr = time.strftime("%H:%M:%S", t)
        GObject.idle_add(self._clock.set_time, timestr)

    def quit(self, *args):
        Gtk.main_quit()

    def run(self):
        self._clock.set_time("00:00:00")
        self._w.fullscreen()
        self._w.show_all()
        Gtk.main()

if __name__ == "__main__":
    b = Bomb()
    b.run()
