from machine import Pin

class SelectButtons:
    def __init__(self, cb):
        self._1_back_btn = Pin(8, Pin.IN, Pin.PULL_UP)
        self._1_front_btn = Pin(9, Pin.IN, Pin.PULL_UP)
        self._2_back_btn = Pin(16, Pin.IN, Pin.PULL_UP)
        self._2_front_btn = Pin(18, Pin.IN, Pin.PULL_UP)
        self._3_back_btn = Pin(19, Pin.IN, Pin.PULL_UP)
        self._3_front_btn = Pin(20, Pin.IN, Pin.PULL_UP)
        self._4_back_btn = Pin(22, Pin.IN, Pin.PULL_UP)
        self._4_front_btn = Pin(21, Pin.IN, Pin.PULL_UP)
        self._cb = cb
        self._last_pressed = None
        self._selected_blinds = set()

    def update(self):
        blind_ids = [
            '1_back',
            '1_front',
            '2_back',
            '2_front',
            '3_back',
            '3_front',
            '4_back',
            '4_front',
        ]

        for blind_id in blind_ids:
            button = getattr(self, f'_{blind_id}_btn')
            if button.value() == 1 and self._last_pressed != blind_id:
                self._last_pressed = blind_id

                if blind_id in self._selected_blinds:
                    self._selected_blinds.remove(blind_id)
                else:
                    self._selected_blinds.add(blind_id)

                self._cb(blind_id, self._selected_blinds)    
            elif button.value() == 0 and self._last_pressed == blind_id:
                self._last_pressed = None