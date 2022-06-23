import ctypes
import yaml

class CallbackUserdata(ctypes.Structure):
    """ Example for user data passed to the callback function. """
    def __init__(self, name):
        self.name = name
        with open("./camera_config/sequence_settings.yml", 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

        self.start_timestamp = None
        self.images_saved = 0