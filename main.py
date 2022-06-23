from CameraWorker import CameraWorker
from Callback import Callbackfuncptr
import os
import time

def connect_cameras(cameras, output = True):
    cameras_not_found = []
    for cam in cameras:
        if not cam.connect():
            cameras_not_found.append(f"{ cam.name } ({ cam.cam_id })")

    if len(cameras_not_found) > 0:
        print("The following cameras couldn't connect:")
        for c in cameras_not_found:
            print(c)
        print("Press [ENTER] to try again (e - exit).")
        return False
    
    else:
        if output:
            print("All cameras connected! Press [ENTER] to start recording (e - exit).")

    return True

def start_cameras(cameras):
    # set_start_timestamp
    ts = round(time.time())
    for cam in cameras:
        cam.set_start_timestamp(ts)
        cam.start_with_callback(Callbackfuncptr)

def stop_cameras(cameras):
    for cam in cameras:
        cam.stop_recording()

config_dir = os.path.join(os.getcwd(), "camera_config")

camera_files = [
    f for f in os.listdir(config_dir)
    if f != "sequence_settings.yml"
]

cameras = []

for cam_file in camera_files:
    cam = CameraWorker(os.path.join(config_dir, cam_file))
    cameras.append(cam)

while True:
    while not connect_cameras(cameras):
        if input() == "e":
            exit()

    if input() == "e":
        exit()

    start_cameras(cameras)
    print("Press [ENTER] to stop recording (e - exit).")
    if input() == "e":
        exit()
    stop_cameras(cameras)