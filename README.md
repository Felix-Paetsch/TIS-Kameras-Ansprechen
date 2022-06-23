This repository builds on [The Imaging Source - Software](https://github.com/TheImagingSource/IC-Imaging-Control-Samples/tree/master/Python/tisgrabber) to create an CLI to software trigger TIS-cameras. For every camera it will periodically take snapshots with the specified settings. These snapshots are synchronised as much as possible.

Requirements
------------
pyyaml `pip install pyyaml`<br>
numpy `pip install numpy`<br>
pillow `pip install pillow`

Usage
-----
1. [Edit the files](#configuration) in `./camera_config`
2. Run `python main.py` in your prefered python enviroment.
3. Press [Enter] to start/stop recording.
4. Type "e" + [Enter] to exit.

After 2. you can continue updating all the config-files to change the camera and snapshot settings. These will update as soon as you stop recording and start again. Note that you can't add new files (cameras) while the programm is running.

Configuration
-------------
The configuration happens in `./camera_config`, there is on specific file for the sequence/snapshot-taking settings and every other file represents one camera.

### Sequence Settings
In `./camera_config/sequence_settings.yml` you have the following parameters:
- `directory`: Output directory where all snapshots are saved.
- `file_prefix`: File prefix of every snapshot (see [here](#output-file-names) for more about file names)
- `start_index`: The snapshots will be numbered starting from `start_index`.
- `time_format_string`: Format the timestamp for when the snapshot was taken. (See [here](https://strftime.org/) for reference.)
- `file_type`: Format in which to save the images. Supported are all types, which are supported by [Pillow]([https://python-pillow.org/](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)). (So including, but not limited to "jpg", "png", "tiff")
- `hz`: How many images to save per second. (E.g. `.5` results in one image every 2 seconds.)

### Camera Files
Every .yml file in `./camera_config` which is not `sequence_settings.yml` is expected to be describing a camera. It should contain the following keys/parameters:
- `id`: Camera Model Name + Serial Number (e.g. `"DFK Z30GP031 41910044"`)
- `cam_name`: How you want to name the camera. This will be used to [name the snapshot files](#output-file-names), so make sure it only contains characters which are valid for file-paths.
- `camera_settings`:
  - `gain`
  - `exposure`:
    - `auto`: Whether to automatically adjust exposure
    - `value`: Exposure value if `auto` is set to false. This can eigther be a float or a range. Specify the latter like `[min, max]`.
    - auto_range: Range in which to automatically adjust `[min, max]`
  - `video_format_str`: Something like `"RGB32 (640x480)"`. See IC Capture for all possible pixel_formats of your device. Specify the width and height in the brackets. Usually both of them have to be devisible by 4, sometimes by 8. 
  - `roi_offset`: Offset of top-left-corner if the viewport is smaller than the possible maximum. `[x_offset, y_offset]`

A template for these files can be found under cam_config.template.yml

##### Binning and Skipping
In order to enable binning or skipping the text “[Binning 2x]” or “[Skipping 2x]” etc must be added to the video format string. For example: `"RGB32 (640x480) [Skipping 2x]"`
The width and the height must be small enough to enable binning and skipping. If 2x is used, then the maximum useable width and height is the sensor’s width / 2 and height / 2.

### Output File Names
The output file names look as follows:
`{ file_prefix }_{ cam_name }_sid{ session_id }_{ formatted_time }_{ image_index }.{ file_type }`
These values are set at:
- `file_prefix`: `sequence_settings.yml`
- `cam_name`: .yml-file of the camera
- `session_id`: unique for each recording sequence (= timestamp at which you press [Enter] in CLI)
- `formatted_time`: `sequence_settings.yml`
- `image_index`: The nth image taken in the current sequence (accounted for sequence_settings.start_index)
- `file_type`: `sequence_settings.yml`
The image_index counts for each camera seperatly. For a given index all images with that index (so from each camera one) were taken as synchronously as possible.
