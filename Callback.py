from CameraWorker import ic
import ctypes
import numpy as np

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
    # print("camera {}". format(pData.index))
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

        data = np.ndarray(buffer=image.contents,
                                dtype=np.uint8,
                                shape=(Height.value,
                                        Width.value,
                                        bpp))

        print(data)
 
Callbackfuncptr = ic.FRAMEREADYCALLBACK(frameReadyCallback)