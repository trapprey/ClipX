import time
import threading
import ctypes
import sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import io
from PIL import Image

import config
from buffer import CircularVideoBuffer

_executor = ThreadPoolExecutor(max_workers=2)


def _set_low_priority():
    if sys.platform == "win32":
        try:
            handle = ctypes.windll.kernel32.GetCurrentThread()
            ctypes.windll.kernel32.SetThreadPriority(handle, -1)
        except Exception:
            pass


def _compress_and_store(frame_np: np.ndarray, timestamp: float, video_buffer: CircularVideoBuffer):
    _set_low_priority()
    img = Image.fromarray(frame_np)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=config.JPEG_QUALITY)
    jpeg_bytes = buf.getvalue()
    with video_buffer.lock:
        video_buffer.frames.append((timestamp, jpeg_bytes))


def start_capture(video_buffer: CircularVideoBuffer):
    def _capture_loop():
        _set_low_priority()

        try:
            import dxcam
            camera = dxcam.create(output_color="RGB")
            use_dxcam = True
            print("[Capture] ✅ dxcam (GPU) — минимальный impact на игру")
        except Exception:
            use_dxcam = False
            print("[Capture] ⚠️  dxcam не найден, использую mss (CPU)")

        frame_interval = 1.0 / config.CAPTURE_FPS

        if use_dxcam:
            camera.start(target_fps=config.CAPTURE_FPS, video_mode=True)
            while True:
                t_start = time.perf_counter()
                frame = camera.get_latest_frame()
                if frame is not None:
                    _executor.submit(_compress_and_store, frame, time.time(), video_buffer)
                elapsed = time.perf_counter() - t_start
                sleep_for = frame_interval - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
        else:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                print(f"[Capture] Экран {monitor['width']}x{monitor['height']} @ {config.CAPTURE_FPS}fps")
                while True:
                    t_start = time.perf_counter()
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)[:, :, :3][:, :, ::-1]
                    _executor.submit(_compress_and_store, frame, time.time(), video_buffer)
                    elapsed = time.perf_counter() - t_start
                    sleep_for = frame_interval - elapsed
                    if sleep_for > 0:
                        time.sleep(sleep_for)

    t = threading.Thread(target=_capture_loop, daemon=True)
    t.start()
    print("[Capture] Запущен")