import os


CAPTURE_FPS       = 60
BUFFER_SECONDS    = 20
JPEG_QUALITY      = 88


SECONDS_BEFORE    = 3
SECONDS_AFTER     = 4


OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Highlights")


CS2_PORT   = 3000
DOTA2_PORT = 3001


CS2_EVENTS   = { 2: "Double_Kill", 3: "Triple_Kill", 4: "Quadro_Kill", 5: "ACE" }
DOTA2_EVENTS = { 2: "Double_Kill", 3: "Triple_Kill", 4: "Ultra_Kill",  5: "RAMPAGE" }


FFMPEG_CRF    = 18
FFMPEG_PRESET = "fast"
FFMPEG_PATH   = "ffmpeg"