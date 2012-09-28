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
    def __init__(self, cb):
        threading.Thread.__init__(self, name="ardunio-thread")
        self._cb = cb
        self.daemon = True

    def run(self):
        val = 59 #should be time.time
        while 1:
            time.sleep(1.0)
            self._cb(val)
            val -= 1 #should be timedelta if serial val changes, blocking read

class Bomb:
    def __init__(self, port='/dev/ttyUSB0'):
        self._w = Gtk.Window()
        self._w.connect("delete-event", self.quit)
        self._clock = Clock()
        self._w.add(self._clock)
        self._thread = SerialThread(self._got_data)
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
