import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd, display
from gui.widgets import Slider, Button, Textbox
from gui.core.writer import Writer
import gui.fonts.arial10 as arial10
from gui.core.colors import *
import close_font
import uasyncio as asyncio

dolittle = lambda *_ : None
class CloseBtn(Button):
    def __init__(self, callback=dolittle, args=()):
        writer = Writer(ssd, close_font)
        self.user_cb = callback
        self.user_args = args
        super().__init__(writer, 2, 128 - 9, shape = CIRCLE, height = 5, callback = self.cb, text = 'A')

    def cb(self, _):
        self.user_cb(self, *self.user_args)

async def wrap(tb, text, lines):
    tb.clear()
    tb.append(text, ntrim = 100, line = 0)
    while True:
        await asyncio.sleep(3)
        if not tb.scroll(lines):
            tb.goto(0)


class DialogBox(Window):

    def __init__(self, writer, text):
        super().__init__(0, 0, 64, 128)

        self.tb = Textbox(writer, 4, 4, 120, nlines = 3, clip = False, bdcolor = BLACK)
        asyncio.create_task(self.text_wrap(text, 3))

        def ok_cb(button):
            Screen.back()

        Button(writer, 40, 37, text='Ok', callback=ok_cb)

    async def text_wrap(self, text, lines):
        await wrap(self.tb, text, lines)

class MainScreen(Screen):

    def __init__(self, remote_control = None):


        super().__init__()

        wri = Writer(ssd, arial10)

        def open_dialog(button):
            print('Opening dialog')
            Screen.change(DialogBox, kwargs = {'writer' : wri, 'text': 'Some very long text, which can span over 3 lines easily and it can be a big deal because I want to be able to read all messages'})

        Button(wri, 18, 2, text='Open', callback=open_dialog)

def test():
    print('Simple demo: button presses print to REPL.')
    Screen.change(MainScreen, args = [])  # A class is passed here, not an instance.

test()