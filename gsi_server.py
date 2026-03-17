import threading
import time
from flask import Flask, request

import config
from buffer import CircularVideoBuffer
from recorder import save_clip




def start_cs2_gsi(video_buffer: CircularVideoBuffer):
    app = Flask("CS2_GSI")
    last_kills = {"value": 0}

    @app.route("/", methods=["POST"])
    def cs2_event():
        data = request.get_json(silent=True) or {}

        try:
            kills = data["player"]["state"]["round_kills"]
        except KeyError:
            return "ok"


        if kills > last_kills["value"]:
            last_kills["value"] = kills

            if kills in config.CS2_EVENTS:
                event_name = config.CS2_EVENTS[kills]
                event_time = time.time()
                print(f"[CS2] 🔥 {event_name}! Записываю клип...")
                save_clip(video_buffer, event_time, "CS2", event_name)


        try:
            phase = data["round"]["phase"]
            if phase in ("freezetime", "over"):
                last_kills["value"] = 0
        except KeyError:
            pass

        return "ok"


    t = threading.Thread(
        target=lambda: app.run(port=config.CS2_PORT, debug=False, use_reloader=False),
        daemon=True
    )
    t.start()
    print(f"[CS2 GSI] Слушаю на порту {config.CS2_PORT}")




def start_dota2_gsi(video_buffer: CircularVideoBuffer):
    app = Flask("DOTA2_GSI")
    last_kills = {"value": 0}

    @app.route("/", methods=["POST"])
    def dota2_event():
        data = request.get_json(silent=True) or {}


        try:
            kills = data["player"]["kill_streak"]
        except KeyError:
            try:
                kills = data["player"]["kills"]   # fallback
            except KeyError:
                return "ok"

        if kills > last_kills["value"]:
            last_kills["value"] = kills

            if kills in config.DOTA2_EVENTS:
                event_name = config.DOTA2_EVENTS[kills]
                event_time = time.time()
                print(f"[Dota2] 🔥 {event_name}! Записываю клип...")
                save_clip(video_buffer, event_time, "Dota2", event_name)


        if kills == 0 and last_kills["value"] > 0:
            last_kills["value"] = 0

        return "ok"

    t = threading.Thread(
        target=lambda: app.run(port=config.DOTA2_PORT, debug=False, use_reloader=False),
        daemon=True
    )
    t.start()
    print(f"[Dota2 GSI] Слушаю на порту {config.DOTA2_PORT}")
