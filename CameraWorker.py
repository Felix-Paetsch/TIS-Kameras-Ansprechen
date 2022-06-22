import tisgrabber as tis
from datetime import datetime
import os
from threading import Thread
from time import sleep
import ctypes
from CallbackUserdata import CallbackUserdata
import yaml

# init tisgrabber
ic = ctypes.cdll.LoadLibrary("./tisgrabber_x64.dll")
tis.declareFunctions(ic)

class CameraWorker:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.name = self.config["camera_name"]
        self.cam_id = self.config["id"]

        self.hGrabber = None
        self.codec = None
        self.save_recording_start_timestamp = None
        self.thread = None
        self.recording = False
        
        self.userdata = CallbackUserdata(self.name)    
        
    def list_properties(self):
        if self.is_connected():
            ic.IC_printItemandElementNames(self.hGrabber)
        else:
            self.connect()
            ic.IC_printItemandElementNames(self.hGrabber)
            self.stop_recording()

    def load_settings(self):
        ic.IC_SetPropertyAbsoluteValue(self.hGrabber, "Gain".encode("utf-8"), "Value".encode("utf-8"), ctypes.c_float(self.config["camera_settings"]["gain"]))

        if self.config["camera_settings"]["exposer"]["auto"]:
            ic.IC_SetPropertySwitch(self.hGrabber, "Exposure".encode("utf-8"), "Auto".encode("utf-8"), 1)
            ic.IC_SetPropertyAbsoluteValueRange(self.hGrabber, "Exposure".encode("utf-8"), "Value".encode("utf-8"), ctypes.c_float(self.config["camera_settings"]["exposer"]["auto_range"][0]), ctypes.c_float(self.config["camera_settings"]["exposer"]["auto_range"][1]))
        else:
            ic.IC_SetPropertySwitch(self.hGrabber, "Exposure".encode("utf-8"), "Auto".encode("utf-8"), 0)
            if type(self.config["camera_settings"]["exposer"]["value"]) == "list":
                ic.IC_SetPropertyAbsoluteValueRange(self.hGrabber, "Exposure".encode("utf-8"), "Value".encode("utf-8"), ctypes.c_float(self.config["camera_settings"]["exposer"]["value"][0]), ctypes.c_float(self.config["camera_settings"]["exposer"]["value"][1]))
            else:
                ic.IC_SetPropertyAbsoluteValue(self.hGrabber, "Exposure".encode("utf-8"), "Value".encode("utf-8"), ctypes.c_float(self.config["camera_settings"]["exposer"]["value"]))

        ic.IC_SetVideoFormat(self.hGrabber, tis.T(self.config["camera_settings"]["video_format"]))
        ic.IC_SetPropertyValue(self.hGrabber, tis.T("Partial scan"),
                   tis.T("X Offset"), self.config["camera_settings"]["roi_offset"][0])
        ic.IC_SetPropertyValue(self.hGrabber, tis.T("Partial scan"),
                   tis.T("Y Offset"), self.config["camera_settings"]["roi_offset"][1])


    def connect(self):
        """
            New hGrabber instance (reference to camera)
        """
        if self.is_connected():
            ic.IC_ReleaseGrabber(self.hGrabber)

        self.hGrabber = ic.IC_CreateGrabber()
        self.load_settings()
        ic.IC_OpenDevByUniqueName(self.hGrabber, tis.T(self.name))
        return ic.IC_IsDevValid(self.hGrabber) == 1
        
    def is_connected(self):
        """
            Does there exist a valid hgrabber Object? (refference to camera)
        """
        return ic.IC_IsDevValid(self.hGrabber) == 1

    def start_recording(self, fn = None, save_every = None):
        """
            Start recording a .avi Video.
            - fn:           <String> save filename
            - save_every:   <Float>  interval in seconds after which to save videos
        """
        if not self.is_connected():
            return False

        self.codec = ic.IC_Codec_Create(tis.T("MJPEG Compressor"))
        ic.IC_SetCodec(self.hGrabber, self.codec)                         # Assign the selected codec to the grabber        

        if save_every:
            self.save_recording_start_timestamp = int(round(datetime.now().timestamp()))
            self.thread = Thread(target = self.run_save_every_thread, args = (fn, save_every, self.save_recording_start_timestamp))
            self.thread.start()
            return True

        if not fn:
            new_fn = f"./recordings/{ self.name }/recording_from_{ datetime.now().strftime('%d-%m-%Y H%H-M%M-S%S') }"
            try:
                os.mkdir(f"./recordings/{ self.name }")
            except:
                pass
        else:
            new_fn = fn

        new_fn = new_fn + ".avi"

        ic.IC_SetAVIFileName(self.hGrabber, tis.T(new_fn))       # Assign file name
        ic.IC_enableAVICapturePause(self.hGrabber, 1)                # Pause avi capture.
        
        if ic.IC_StartLive(self.hGrabber, 1) == tis.IC_SUCCESS:
            ic.IC_enableAVICapturePause(self.hGrabber, 0)         # Unpause avi capture.
            self.recording = True

            return True
        else:
            return False

             
    # function to create threads
    def run_save_every_thread(self, fn, save_every, start_timestamp):
        n = 0
        r = True
        self.recording = True
        while r and start_timestamp == self.save_recording_start_timestamp and self.is_recording():
            new_fn = fn if not fn else f"{ fn }_{ n }"

            if n == 0:
                r = self.start_recording(new_fn)
            elif not fn:
                r = self.make_recording_checkpoint()
            else:
                r = self.make_recording_checkpoint(new_fn)

            n += 1
            
            st = round(datetime.now().timestamp())
            while (start_timestamp == self.save_recording_start_timestamp) and (st + save_every > round(datetime.now().timestamp())):
                sleep(1)

        ic.IC_StopLive(self.hGrabber)
        self.recording = False


    def is_recording(self):
        """
            is_connected && camera is active
        """
        return self.is_connected() and self.recording
        
    def make_recording_checkpoint(self, new_fn = None):
        """
            Call this function to end old recording (finish .avi-file) and start a new one
            - new_fn: <String> Filename of newly started Video
        """
        if self.is_recording():
            ic.IC_StopLive(self.hGrabber)
            self.recording = False
            return self.start_recording(new_fn)

        return False

    def stop_recording(self):
        """
            End either video recording or start_with_callback
            (+ free memory)
        """
        if self.is_recording():
            self.save_recording_start_timestamp = None
            if self.thread:
                self.thread.join()
                self.thread = None 
            else:
                ic.IC_StopLive(self.hGrabber)

        if self.is_connected():
            ic.IC_ReleaseGrabber(self.hGrabber)

        self.hGrabber = None

        if not self.codec is None:
            ic.IC_Codec_Release(self.codec)
            
        self.recording = False

    def start_with_callback(self, Callbackfuncptr):
        if(ic.IC_IsDevValid(self.hGrabber)):
            ic.IC_SetFrameReadyCallback(self.hGrabber, Callbackfuncptr, self.userdata)
            ic.IC_SetContinuousMode(self.hGrabber, 0)
            self.recording = True
            return ic.IC_StartLive(self.hGrabber, 1) == tis.IC_SUCCESS