from CameraWorker import ic
import ctypes
import numpy as np
import time
from datetime import datetime
from PIL import Image
import os

def frameReadyCallback(hGrabber, pBuffer, framenumber, pData):
    """ This is an example callback function for image processing with 
        opencv. The image data in pBuffer is converted into a cv Matrix
        and with cv.mean() the average brightness of the image is
        measuered

    :param: hGrabber: This is the real pointer to the grabber object.
    :param: pBuffer : Pointer to the first pixel's first byte
    :param: framenumber : Number of the frame since the stream started
    :param: pData : Pointer to additional user data structure
    """
    
    ts = time.time()
    if (pData.start_timestamp + pData.images_saved / pData.data["hz"] > ts):
        return

    Width = ctypes.c_long()
    Height = ctypes.c_long()
    BitsPerPixel = ctypes.c_int()
    colorformat = ctypes.c_int()

    # Query the image description values
    ic.IC_GetImageDescription(hGrabber, Width, Height, BitsPerPixel, colorformat)

    # Calculate the buffer size
    bpp = int(BitsPerPixel.value/8.0)
    buffer_size = Width.value * Height.value * bpp

    if buffer_size > 0:
        image = ctypes.cast(pBuffer, 
                            ctypes.POINTER(
                                ctypes.c_ubyte * buffer_size))

        Image.fromarray(
            np.ndarray(buffer=image.contents,
                        dtype=np.uint8,
                        shape=(Height.value,
                                Width.value,
                                bpp))
        ).save(os.path.join(
            pData.data["directory"],
            f'{ pData.data["file_prefix"] }_{ pData.name }_sid{ pData.start_timestamp }_{ datetime.fromtimestamp(ts).strftime(pData.data["time_format_string"]) }_{ pData.images_saved + pData.data["start_index"] }.{ pData.data["file_type"] }'
        ))

        pData.images_saved += 1
 
Callbackfuncptr = ic.FRAMEREADYCALLBACK(frameReadyCallback)