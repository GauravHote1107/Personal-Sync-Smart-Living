import requests


class NodeClient:
    _BASE_URL = "http://192.168.4.1/"
    _DEFAULT_VALUES = {"D1": 0, "D2": 0, "D3": 0, "D4": 0, "D5": 1024, "D6": 0, "D7": 0, "D8": 0}

    def __init__(self):
        self.values_cache = requests.get(self._BASE_URL + "state").json()

    def update_pin(self, pin: str, state: int):
        if self.values_cache[pin] == state:
            return

        requests.get(self._BASE_URL + f"pin/{pin}/{state}")
        self.values_cache[pin] = state

        print(f"Updated {pin} to {state}.")

    def reset_pin(self, pin: str):
        self.update_pin(pin, self._DEFAULT_VALUES[pin])
