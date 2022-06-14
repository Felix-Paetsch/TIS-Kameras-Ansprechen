from CameraWorker import CameraWorker
from Callback import Callbackfuncptr

cam1 = CameraWorker("DFK 33GP1300e 12220738", "./camera_config/cam1.yml")
cam1.connect()
cam1.start_with_callback(Callbackfuncptr)
cam1.load_settings()
cam1.stop_recording()