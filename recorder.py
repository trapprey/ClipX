import os
import subprocess
import threading
import time
from datetime import datetime

import config
from buffer import CircularVideoBuffer


def save_clip(video_buffer: CircularVideoBuffer, event_time: float, game: str, event_name: str):
    def _worker():
        time.sleep(config.SECONDS_AFTER + 0.5)
        frames = video_buffer.get_clip(event_time)
        if not frames:
            print("[Recorder] Буфер пустой, клип не сохранён.")
            return
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        ts_str   = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{game}_{event_name}_{ts_str}.mp4"
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        _encode_clip(frames, filepath)
        print(f"[Recorder] ✅ Клип сохранён: {filepath}")

    threading.Thread(target=_worker, daemon=True).start()


def _real_fps(frames):
    if len(frames) < 2:
        return config.CAPTURE_FPS
    duration = frames[-1][0] - frames[0][0]
    if duration <= 0:
        return config.CAPTURE_FPS
    return max(10.0, min((len(frames) - 1) / duration, config.CAPTURE_FPS))


def _build_cmd_gpu(filepath, fps):
    return [
        config.FFMPEG_PATH, "-y",
        "-f", "image2pipe", "-vcodec", "mjpeg",
        "-r", f"{fps:.3f}", "-i", "pipe:0",
        "-vcodec", "h264_nvenc", "-preset", "p4",
        "-rc", "vbr", "-cq", str(config.FFMPEG_CRF),
        "-b:v", "0", "-pix_fmt", "yuv420p", filepath,
    ]


def _build_cmd_cpu(filepath, fps):
    return [
        config.FFMPEG_PATH, "-y",
        "-f", "image2pipe", "-vcodec", "mjpeg",
        "-r", f"{fps:.3f}", "-i", "pipe:0",
        "-vcodec", "libx264", "-preset", config.FFMPEG_PRESET,
        "-crf", str(config.FFMPEG_CRF),
        "-pix_fmt", "yuv420p", filepath,
    ]


def _run_ffmpeg(cmd, frames):
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _, jpeg_bytes in frames:
            proc.stdin.write(jpeg_bytes)
        proc.stdin.close()
        proc.wait()
        return proc.returncode == 0
    except FileNotFoundError:
        print("[Recorder] ❌ ffmpeg не найден!")
        return False
    except Exception as e:
        print(f"[Recorder] ❌ Ошибка: {e}")
        return False


def _encode_clip(frames, filepath):
    fps = _real_fps(frames)
    print(f"[Recorder] 📹 Кадров: {len(frames)}, FPS: {fps:.1f}, длина: {len(frames)/fps:.1f}с")
    if _run_ffmpeg(_build_cmd_gpu(filepath, fps), frames):
        print("[Recorder] 🎮 Закодировано на GPU (NVENC)")
        return
    print("[Recorder]   NVENC недоступен, переключаюсь на CPU...")
    _run_ffmpeg(_build_cmd_cpu(filepath, fps), frames)