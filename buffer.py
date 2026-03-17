import collections
import threading
import numpy as np

import config


class CircularVideoBuffer:
    def __init__(self):
        max_frames = config.BUFFER_SECONDS * config.CAPTURE_FPS
        self.frames: collections.deque = collections.deque(maxlen=max_frames)
        self.lock = threading.Lock()

    def add_frame(self, frame_np: np.ndarray, timestamp: float):
        pass

    def get_clip(self, event_time: float) -> list[tuple[float, bytes]]:
        start = event_time - config.SECONDS_BEFORE
        end   = event_time + config.SECONDS_AFTER
        with self.lock:
            return [
                (ts, data) for ts, data in self.frames
                if start <= ts <= end
            ]

    def frame_count(self) -> int:
        with self.lock:
            return len(self.frames)