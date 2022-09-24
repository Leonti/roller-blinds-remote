import time
from core.nrf import Sender

def blind_id_to_client(blind_id):
    split = blind_id.split('_')
    side = 0 if split[1] == 'front' else 1
    return (int(split[0], 10) - 1, side)


commands = {
    'UP_FOR_LIMIT': 1,
    'STOP_AND_SET_TOP_LIMIT': 2,
    'GO_DOWN_FOR_LIMIT': 3,
    'STOP_AND_SET_BOTTOM_LIMIT': 4,
    'OPEN_BLINDS': 5,
    'CLOSE_BLINDS': 6,
    'MOVE_BLINDS_TO': 7,
    'READ_RESPONSE': 8,
    'PREPARE_STATUS': 9,
    'PREPARE_SETTINGS': 10,
    'UPDATE_SETTINGS': 11,
}

class RemoteControl:

    def __init__(self):
        self._sender = Sender()
        print('Creating remote control')

    def go_up_for_limit(self, blind_id):
        print(f'Going up for limit for {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        return self._sender.send_with_retries(client_id, bytes(f"{commands['UP_FOR_LIMIT']}:{side}", 'utf-8'))

    def stop_and_set_top_limit(self, blind_id):
        print(f'Stop and set top limit for {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        return self._sender.send_with_retries(client_id, bytes(f"{commands['STOP_AND_SET_TOP_LIMIT']}:{side}", 'utf-8'))

    def go_down_for_limit(self, blind_id):
        print(f'Going down for limit for {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        return self._sender.send_with_retries(client_id, bytes(f"{commands['GO_DOWN_FOR_LIMIT']}:{side}", 'utf-8'))

    def stop_and_set_bottom_limit(self, blind_id):
        print(f'Stop and set bottom limit for {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        return self._sender.send_with_retries(client_id, bytes(f"{commands['STOP_AND_SET_BOTTOM_LIMIT']}:{side}", 'utf-8'))

    def open_blinds(self, blinds):
        print(f'Opening blinds {blinds}')
        results = []
        for blind_id in blinds:
            client_id, side = blind_id_to_client(blind_id)
            if self._sender.send_with_retries(client_id, bytes(f"{commands['MOVE_BLINDS_TO']}:{side}:0", 'utf-8')):
                results.append(blind_id)
        return results

    def close_blinds(self, blinds):
        print(f'Closing blinds {blinds}')
        results = []
        for blind_id in blinds:
            client_id, side = blind_id_to_client(blind_id)
            if self._sender.send_with_retries(client_id, bytes(f"{commands['MOVE_BLINDS_TO']}:{side}:100", 'utf-8')):
                results.append(blind_id)
        return results

    def move_blinds_to(self, blinds, set_point):
        print(f'Moving blinds to {blinds} {set_point}')
        results = []
        for blind_id in blinds:
            client_id, side = blind_id_to_client(blind_id)
            if self._sender.send_with_retries(client_id, bytes(f"{commands['MOVE_BLINDS_TO']}:{side}:{set_point}", 'utf-8')):
                results.append(blind_id)
        return results

    def read_settings(self, blind_id):
        print(f'Reading settings {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        prepare_response = self._sender.send_with_retries(client_id, bytes(f"{commands['PREPARE_SETTINGS']}:{side}", 'utf-8'))
        if not prepare_response:
            return prepare_response
        time.sleep(0.1)    
        settings_raw = self._sender.send_with_retries(client_id, bytes(f"{commands['READ_RESPONSE']}", 'utf-8'))
        print(settings_raw)
        settings_split = settings_raw.decode('utf-8').split(':')
        return {
            'bottom_limit': settings_split[0],
            'slowdown_percent': settings_split[1],
            'manual_speed_up': settings_split[2],
            'manual_speed_down': settings_split[3],
        }

    def update_settings(self, blind_id, bottom_limit, slowdown_percent, manual_speed_up, manual_speed_down):
        print(f'Storing settings {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        self._sender.send_with_retries(client_id, bytes(f"{commands['UPDATE_SETTINGS']}:{side}:{bottom_limit}:{slowdown_percent}:{manual_speed_up}:{manual_speed_down}", 'utf-8'))

    def read_status(self, blind_id):
        print(f'Reading status {blind_id}')
        client_id, side = blind_id_to_client(blind_id)
        prepare_response = self._sender.send_with_retries(client_id, bytes(f"{commands['PREPARE_STATUS']}:{side}", 'utf-8'))
        if not prepare_response:
            return prepare_response
        time.sleep(0.1)    
        status_raw = self._sender.send_with_retries(client_id, bytes(f"{commands['READ_RESPONSE']}", 'utf-8'))
        print(status_raw)
        status_split = status_raw.decode('utf-8').split(':')
        return {
            'position': status_split[0],
            'goal': status_split[1],
            'is_goal_reached': status_split[2],
        }            