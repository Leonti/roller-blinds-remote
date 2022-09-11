class RemoteControl:

    def __init__(self):
        print('Creating remote control')

    def go_up_for_limit(self, blind_id):
        print(f'Going up for limit for {blind_id}')

    def stop_and_set_top_limit(self, blind_id):
        print(f'Stop and set top limit for {blind_id}')

    def go_down_for_limit(self, blind_id):
        print(f'Going down for limit for {blind_id}')

    def stop_and_set_bottom_limit(self, blind_id):
        print(f'Stop and set bottom limit for {blind_id}')

    def open_blinds(self, blinds):
        print(f'Opening blinds {blinds}')

    def close_blinds(self, blinds):
        print(f'Closing blinds {blinds}')

    def move_blinds_to(self, blinds, set_point):
        print(f'Moving blinds to {blinds} {set_point}')