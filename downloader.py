from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import ffmpeg  # from ffmpeg-python
import re

# Set paths
SAVE_PATH = "C:/Users/scamp/Videos/Youtube/"
TEMP_VIDEO_FILE = os.path.join(SAVE_PATH, "temp.mp4")
TEMP_AUDIO_FILE = os.path.join(SAVE_PATH, "temp.m4a")
FILE_EXTENSION = ".mp4"
PREFERRED_RESOLUTION = "1080"

# ANSI color codes
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
OFF = "\033[0;0m"

# Ensure save directory exists
os.makedirs(SAVE_PATH, exist_ok=True)

def sanitize_filename(s):
    # Remove or replace invalid Windows filename characters
    return re.sub(r'[<>:"/\\|?*]', '', s)


def find_best_resolution(yt):
    preferred_video_itag = ""
    best_resolution = 0

    for stream in yt.fmt_streams:
        if stream.resolution:
            try:
                res = int(stream.resolution[:-1])
                if res > best_resolution:
                    preferred_video_itag = stream.itag
                    best_resolution = res
                if stream.resolution[:-1] == PREFERRED_RESOLUTION:
                    preferred_video_itag = stream.itag
                    print(f"{GREEN}Using preferred video itag = {preferred_video_itag}{OFF}")
                    break
            except ValueError:
                continue
    return preferred_video_itag

queue = [
    "https://www.youtube.com/watch?v=wto2oyfD2iY",
    # "https://www.youtube.com/watch?v=va-YHeytvFQ&t=99s",
]

for url in queue:
    print(url)

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(YELLOW + yt.title + OFF)

        original_title = sanitize_filename(yt.title)
        output_file = os.path.join(SAVE_PATH, original_title + FILE_EXTENSION)
        preferred_video_itag = find_best_resolution(yt)

        # Download video
        try:
            video = yt.streams.get_by_itag(preferred_video_itag)
            video.download(output_path=SAVE_PATH, filename="temp.mp4")
        except Exception as e:
            print(RED + f"Video download failed: {e}" + OFF)

        # Download audio
        try:
            audio = yt.streams.get_audio_only()
            print(f"{CYAN}Using preferred audio itag = {audio.itag}{OFF}")
            audio.download(output_path=SAVE_PATH, filename="temp.m4a")
        except Exception as e:
            print(RED + f"Audio download failed: {e}" + OFF)

        # Debug file presence
        print("Checking downloaded files:")
        print("Video exists:", os.path.exists(TEMP_VIDEO_FILE))
        print("Audio exists:", os.path.exists(TEMP_AUDIO_FILE))

        if os.path.exists(TEMP_VIDEO_FILE) and os.path.exists(TEMP_AUDIO_FILE):
            output_file = os.path.join(SAVE_PATH, original_title + FILE_EXTENSION)
            ffmpeg.output(
                ffmpeg.input(TEMP_VIDEO_FILE),
                ffmpeg.input(TEMP_AUDIO_FILE),
                output_file,
                vcodec="copy",
                acodec="aac"
            ).run(overwrite_output=True)
            print(GREEN + f"Finished: {output_file}" + OFF)
        else:
            print(RED + "Skipping merge: one or both temp files missing." + OFF)

        # Clean up
        for f in [TEMP_VIDEO_FILE, TEMP_AUDIO_FILE]:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        print(RED + f"Unexpected error: {e}" + OFF)
