from CameraWorker import CameraWorker
from Callback import Callbackfuncptr
import os

def connect_cameras(cameras):
    cameras_not_found = []
    for cam in cameras:
        if not cam.connect():
            cameras_not_found.append(f"{ cam.name } ({ cam.cam_id })")

    if len(cameras_not_found) > 0:
        print("The following cameras couldn't connect:")
        for c in cameras_not_found:
            print(c)
        print("Press any key to try again (e - exit).")
        return False
    
    else:
        print("All cameras connected! Press any key to start recording (e - exit).")

    return True

config_dir = os.path.join(os.getcwd(), "camera_config")

camera_files = [
    f for f in os.listdir(config_dir)
    if f != "sequence_settings.yml"
]

cameras = []

for cam_file in camera_files:
    cam = CameraWorker(os.path.join(config_dir, cam_file))
    cameras.append(cam)

while not connect_cameras():
    if input() == "e":
        exit()

if input() == "e":
    exit()

# start_recording

# start, stop, ... cameras