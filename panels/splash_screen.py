import gi
import logging
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango

from ks_includes.screen_panel import ScreenPanel

def create_panel(*args):
    return SplashScreenPanel(*args)

class SplashScreenPanel(ScreenPanel):
    box = None

    def __init__(self, screen, title, back=True):
        super().__init__(screen, title, back)

        self.layout = Gtk.Layout()
        self.layout.set_size(self._screen.width, self._screen.height)

    def initialize(self, panel_name):
        _ = self.lang.gettext

        image = self._gtk.Image("klipper.svg", None, 3.2, 3.2)

        self.labels['text'] = Gtk.Label(_("Initializing printer..."))
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)


        self.labels['actions'] = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.labels['actions'].set_hexpand(True)
        self.labels['actions'].set_vexpand(False)
        self.labels['actions'].set_halign(Gtk.Align.CENTER)
        self.labels['actions'].set_homogeneous(True)

        scroll = Gtk.ScrolledWindow()
        scroll.set_property("overlay-scrolling", False)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.labels['text'])

        info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        info.pack_start(image, False, True, 8)
        info.pack_end(scroll, True, True, 8)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main.pack_start(info, True, True, 8)
        main.pack_end(self.labels['actions'], False, False, 0)

        self.content.add(main)

    def update_text(self, text):
        self.labels['text'].set_text(text)
        self.clear_action_bar()

    def clear_action_bar(self):
        for child in self.labels['actions'].get_children():
            self.labels['actions'].remove(child)

    def show_restart_buttons(self):
        _ = self.lang.gettext

        if "firmware_restart" not in self.labels:
            self.labels['menu'] = self._gtk.ButtonImage("settings", _("Menu"), "color4")
            self.labels['menu'].connect("clicked", self._screen._go_to_submenu, "")
            self.labels['power'] = self._gtk.ButtonImage("shutdown", _("Power On Printer"), "color3")
            self.labels['restart'] = self._gtk.ButtonImage("refresh", _("Restart"), "color1")
            self.labels['restart'].connect("clicked", self.restart)
            self.labels['firmware_restart'] = self._gtk.ButtonImage("refresh", _("Firmware Restart"), "color2")
            self.labels['firmware_restart'].connect("clicked", self.firmware_restart)

        self.clear_action_bar()

        devices = [i for i in self._printer.get_power_devices() if i.lower().startswith('printer')] if (
            self._printer is not None) else []
        logging.debug("Power devices: %s" % devices)
        if len(devices) > 0:
            logging.debug("Adding power button")
            self.labels['power'].connect("clicked", self.power_on, devices)
            self.labels['actions'].add(self.labels['power'])

        self.labels['actions'].add(self.labels['restart'])
        self.labels['actions'].add(self.labels['firmware_restart'])
        self.labels['actions'].add(self.labels['menu'])
        self.labels['actions'].show_all()

    def firmware_restart(self, widget):
        self._screen._ws.klippy.restart_firmware()

    def power_on(self, widget, devices):
        for device in devices:
            self._screen._ws.klippy.power_device_on(device)

    def restart(self, widget):
        self._screen._ws.klippy.restart()
