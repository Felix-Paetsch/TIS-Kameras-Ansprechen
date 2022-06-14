import ctypes

class CallbackUserdata(ctypes.Structure):
    """ Example for user data passed to the callback function. """
    def __init__(self, name):
        self.name = name
        self.Value1 = 42
        self.Value2 = 0
        self.camera = None      # Reference to a camera/grabber object