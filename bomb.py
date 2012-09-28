import threading

import time
import serial

from gi.repository import Gtk, Gdk, GObject

GObject.threads_init()
Gdk.threads_init()

class Clock(Gtk.EventBox):
    def __init__(self, size=300):
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
            self._cb(int(val) if val else 0)
        self._ser.close()

class Bomb:
    def __init__(self, port='/dev/ttyACM0'):
        self._w = Gtk.Window()
        self._w.connect("delete-event", self.quit)
        self._clock = Clock()
        self._w.add(self._clock)
        self._thread = SerialThread(port, self._got_data)
        self._thread.start()

    def _got_data(self, val):
        timestr = "00:00:%d" % val #strftime
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
