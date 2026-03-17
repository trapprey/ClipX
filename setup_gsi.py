
import os
import sys


CS2_CFG_CONTENT = """
"highlight_recorder"
{
    "uri"        "http://127.0.0.1:3000"
    "timeout"    "5.0"
    "buffer"     "0.1"
    "throttle"   "0.5"
    "heartbeat"  "10.0"
    "data"
    {
        "player_state"      "1"
        "round"             "1"
        "player_match_stats" "1"
    }
}
"""


DOTA2_CFG_CONTENT = """
"highlight_recorder"
{
    "uri"        "http://127.0.0.1:3001"
    "timeout"    "5.0"
    "buffer"     "0.1"
    "throttle"   "0.5"
    "heartbeat"  "10.0"
    "data"
    {
        "provider"     "1"
        "map"          "1"
        "player"       "1"
        "hero"         "1"
        "abilities"    "0"
        "items"        "0"
    }
}
"""


def find_steam_path():

    candidates = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/Library/Application Support/Steam"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    return None


def setup_cs2(steam_path: str):
    cfg_path = os.path.join(
        steam_path,
        "steamapps", "common",
        "Counter-Strike Global Offensive",
        "game", "csgo", "cfg",
        "gamestate_integration_highlight_recorder.cfg"
    )
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    with open(cfg_path, "w") as f:
        f.write(CS2_CFG_CONTENT.strip())
    print(f"[CS2] ✅ GSI конфиг создан:\n     {cfg_path}")


def setup_dota2(steam_path: str):
    cfg_path = os.path.join(
        steam_path,
        "steamapps", "common",
        "dota 2 beta",
        "game", "dota", "cfg",
        "gamestate_integration_highlight_recorder.cfg"
    )
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    with open(cfg_path, "w") as f:
        f.write(DOTA2_CFG_CONTENT.strip())
    print(f"[Dota2] ✅ GSI конфиг создан:\n        {cfg_path}")


def main():
    print("=" * 50)
    print("  GSI Setup — Highlight Recorder")
    print("=" * 50)

    steam = find_steam_path()

    if not steam:
        print("❌ Steam не найден автоматически.")
        steam = input("Введи путь к папке Steam вручную: ").strip()
        if not os.path.isdir(steam):
            print("❌ Папка не существует. Выход.")
            sys.exit(1)

    print(f"✅ Steam найден: {steam}\n")


    try:
        setup_cs2(steam)
    except Exception as e:
        print(f"[CS2] ⚠️  Ошибка: {e}")


    try:
        setup_dota2(steam)
    except Exception as e:
        print(f"[Dota2] ⚠️  Ошибка: {e}")

    print()
    print("🎉 Готово! Теперь:")
    print("   1. Перезапусти CS2 и/или Dota 2")
    print("   2. Запусти: python main.py")
    print("   3. Заходи в игру и делай жёсткие моменты 🔥")


if __name__ == "__main__":
    main()
