# simple.py Minimal micro-gui demo.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd, display
from gui.widgets import Slider, Button, Textbox
from gui.core.writer import Writer
import gui.fonts.arial10 as arial10
from gui.core.colors import *
import close_font
from machine import Pin
import uasyncio as asyncio
from remote_control import RemoteControl
from select_buttons import SelectButtons

dolittle = lambda *_ : None
class CloseBtn(Button):
    def __init__(self, callback=dolittle, args=()):
        writer = Writer(ssd, close_font)
        self.user_cb = callback
        self.user_args = args
        super().__init__(writer, 2, 128 - 9, shape = CIRCLE, height = 5, callback = self.cb, text = 'A')

    def cb(self, _):
        self.user_cb(self, *self.user_args)

def draw_indicators(display, selected_blinds):
    for pair in range(0, 4):
        if f'{pair + 1}_back' in selected_blinds:
            display.fill_rect(2 + pair * 10, 2, 8, 4, WHITE)
        else:
            display.fill_rect(2 + pair * 10, 2, 8, 4, BLACK)
            display.rect(2 + pair * 10, 2, 8, 4, WHITE)
        if f'{pair + 1}_front' in selected_blinds:      
            display.fill_rect(2 + pair * 10, 7, 8, 4, WHITE)
        else:
            display.fill_rect(2 + pair * 10, 7, 8, 4, BLACK)
            display.rect(2 + pair * 10, 7, 8, 4, WHITE)

async def wrap(tb, text, lines):
    tb.clear()
    tb.append(text, ntrim = 100, line = 0)
    while True:
        await asyncio.sleep(3)
        if not tb.scroll(lines):
            tb.goto(0)

class LimistSetScreen(Screen):

    def __init__(self, remote_control):
        super().__init__()

        def ok_cb(button):
            Screen.change(MainScreen, args=[remote_control])

        wri = Writer(ssd, arial10)
        self.tb = Textbox(wri, 2, 2, 124, nlines = 3, clip = False, bdcolor = BLACK)
        asyncio.create_task(self.text_wrap('The limits are set now. You can repeat the procedure to adjust limits at any time.', 3))

        Button(wri, 42, 2, text='Ok', callback=ok_cb)

    async def text_wrap(self, text, lines):
        await wrap(self.tb, text, lines)

class GoingDownScreen(Screen):

    def __init__(self, remote_control, blind_id):
        super().__init__()

        def bottom_reached_cb(button):
            remote_control.stop_and_set_bottom_limit(blind_id)
            Screen.change(LimistSetScreen, args=[remote_control])

        wri = Writer(ssd, arial10)
        self.tb = Textbox(wri, 2, 2, 124, nlines = 3, clip = False, bdcolor = BLACK)
        asyncio.create_task(self.text_wrap("The blinds should be going down now. They will stop after pressing 'Bottom Reached'.", 3))
        Button(wri, 42, 2, text='Bottom Reached', callback=bottom_reached_cb)

    async def text_wrap(self, text, lines):
        await wrap(self.tb, text, lines)

class SetBottomConfirmation(Screen):

    def __init__(self, remote_control, blind_id):
        super().__init__()

        def ok_cb(button):
            remote_control.go_down_for_limit(blind_id)
            Screen.change(GoingDownScreen, args=[remote_control, blind_id])

        def cancel_cb(button):
            Screen.change(MainScreen, args=[remote_control])

        wri = Writer(ssd, arial10)
        self.tb = Textbox(wri, 2, 2, 124, nlines = 3, clip = False, bdcolor = BLACK)
        asyncio.create_task(self.text_wrap("If you are happy with the top limit press 'Ok' to go down and set the bottom limit", 3))

        Button(wri, 42, 2, text='Ok', callback=ok_cb)
        Button(wri, 42, 60, text='Cancel', callback=cancel_cb)

    async def text_wrap(self, text, lines):
        await wrap(self.tb, text, lines)

class GoingUpScreen(Screen):

    def __init__(self, remote_control, blind_id):
        super().__init__()

        def top_reached_cb(button):
            remote_control.stop_and_set_top_limit(blind_id)
            Screen.change(SetBottomConfirmation, args=[remote_control, blind_id])

        wri = Writer(ssd, arial10)
        self.tb = Textbox(wri, 2, 2, 124, nlines = 3, clip = False, bdcolor = BLACK)
        asyncio.create_task(self.text_wrap("Blinds should go up now. Press 'Top Reached' to stop and set the top limit", 3))

        Button(wri, 42, 2, text='Top Reached', callback=top_reached_cb)

    async def text_wrap(self, text, lines):
        await wrap(self.tb, text, lines)

class SetTopConfirmation(Screen):

    def __init__(self, selected_blinds, remote_control, blind_id):
        super().__init__()

        self._selected_blinds = selected_blinds

        def ok_cb(button):
            remote_control.go_up_for_limit(blind_id)
            Screen.change(GoingUpScreen, args=[remote_control, blind_id])

        def cancel_cb(button):
            Screen.change(MainScreen, args=[remote_control])

        wri = Writer(ssd, arial10)
        self.tb = Textbox(wri, 17, 2, 124, nlines = 2, clip = False, bdcolor = BLACK)
        asyncio.create_task(self.text_wrap("Make sure that the blind is not too close to the top. Press 'Ok' to go up now.", 2))

        Button(wri, 42, 2, text='Ok', callback=ok_cb)
        Button(wri, 42, 60, text='Cancel', callback=cancel_cb)

    def after_open(self):
        draw_indicators(display, self._selected_blinds)

    async def text_wrap(self, text, lines):
        await wrap(self.tb, text, lines)

class ConfigScreen(Screen):

    def __init__(self, selected_blinds, remote_control):
        super().__init__()

        self._selected_blinds = selected_blinds

        def set_limits_cb(button, arg):
            blind_id = list(self._selected_blinds)[0]
            Screen.change(SetTopConfirmation, args = [self._selected_blinds, remote_control, blind_id])

        wri = Writer(ssd, arial10)
        Button(wri, 18, 2, text='Set Limits', callback=set_limits_cb, args=('set top',))
        CloseBtn(lambda _: Screen.change(MainScreen, args=[remote_control]))

    def after_open(self):
        draw_indicators(display, self._selected_blinds)

class CustomPositionScreen(Screen):

    def __init__(self, selected_blinds, remote_control):
        super().__init__()

        self._selected_blinds = selected_blinds

        wri = Writer(ssd, arial10)
        slider = Slider(wri, 2, 80, height = 60, value=0.5, min_delta=0.1, max_delta=0.2)

        def move_blinds_cb(button):
            position = round((1.0 - slider.value()) * 100)
            remote_control.move_blinds_to(self._selected_blinds, position)
            Screen.change(MainScreen, args=[remote_control])

        Button(wri, 18, 2, text='Move', callback=move_blinds_cb)
        Button(wri, 42, 2, text='Cancel', callback=lambda _: Screen.back())

    def after_open(self):
        draw_indicators(display, self._selected_blinds)

class MainScreen(Screen):

    def __init__(self, remote_control = None):
        if remote_control is None:
            remote_control = RemoteControl()
        self._selected_blinds = ()

        def open_cb(button):
            if len(self._selected_blinds) == 1:
                remote_control.open_blinds(self._selected_blinds)

        def close_cb(button):
            if len(self._selected_blinds) == 1:
                remote_control.close_blinds(self._selected_blinds)

        def config_screen_callback(button):
            if len(self._selected_blinds) == 1:
                Screen.change(ConfigScreen, args = [self._selected_blinds, remote_control])

        def custom_cb(button):
            if len(self._selected_blinds) == 1:
                Screen.change(CustomPositionScreen, args = [self._selected_blinds, remote_control])

        def blind_selected(blind_id, selected_blinds):
            print('blind selected:', blind_id)
            draw_indicators(display, selected_blinds)
            self._selected_blinds = selected_blinds

        super().__init__()
        self._select_buttons = SelectButtons(blind_selected)

        wri = Writer(ssd, arial10)
        Button(wri, 18, 2, text='Open', callback=open_cb)
        Button(wri, 18, 60, text='Custom', callback=custom_cb)
        Button(wri, 42, 2, text='Close', callback=close_cb)
        Button(wri, 42, 60, text='Setup', callback=config_screen_callback)

    def after_open(self):
        draw_indicators(display, ())
        self.reg_task(self.check_select_buttons(), True)

    async def check_select_buttons(self):
        while True:
            self._select_buttons.update()
            await asyncio.sleep(0.001)

def test():
    print('Simple demo: button presses print to REPL.')
    Screen.change(MainScreen, args = [])  # A class is passed here, not an instance.

test()