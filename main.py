import time
import os
import sys
import ctypes

from buffer import CircularVideoBuffer
from capture import start_capture
from gsi_server import start_cs2_gsi, start_dota2_gsi
import config


def set_process_low_priority():
    if sys.platform == "win32":
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x4000)
            print("[Main] ✅ Приоритет процесса: низкий (игра важнее)")
        except Exception:
            pass


def main():
    print("=" * 50)
    print("  🎮 Highlight Recorder v1.1")
    print("  CS2 + Dota 2")
    print("=" * 50)
    print(f"  Буфер:    {config.BUFFER_SECONDS} сек")
    print(f"  Клип:     -{config.SECONDS_BEFORE}s / +{config.SECONDS_AFTER}s от события")
    print(f"  Папка:    {config.OUTPUT_DIR}")
    print("=" * 50)

    set_process_low_priority()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    video_buffer = CircularVideoBuffer()
    start_capture(video_buffer)

    print("[Main] Заполняю буфер...")
    time.sleep(3)
    print(f"[Main] Буфер готов — {video_buffer.frame_count()} кадров в памяти")

    start_cs2_gsi(video_buffer)
    start_dota2_gsi(video_buffer)

    print()
    print("✅ Прога запущена! Можешь открывать игру.")
    print("   Клипы сохраняются в папку Highlights на рабочем столе.")
    print("   Нажми Ctrl+C чтобы остановить.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Завершение...")


if __name__ == "__main__":
    main()