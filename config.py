import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8757096551:AAH8AU5FxY2-Zr1AgMek9_nM8fevB45gWJk")

CHANNELS = [
    {"chat_id": -1003265919438, "username": "seimuzcrack", "label": "СЕЙМУЗ КРЯК"},
    {"chat_id": -1003436435497, "username": "nebulaclientt", "label": "NEBULA CLIENT"},
    {"chat_id": -1003731864428, "username": "seimuz_mine", "label": "СЕЙМУЗ ЖИЗНЬ"},
]

CHEATS = {
    "wild": {
        "name": "КРЯК WILD CLIENT",
        "files": [
            "cheats/fabric-api-0.136.1-1.21.8.jar",
            "cheats/w1ld-cracked.jar",
        ],
    },
    "wexside": {
        "name": "КРЯК WEXSIDE CLIENT",
        "files": [
            "cheats/wexside-client-1.0.0.jar",
        ],
    },
    "essence": {
        "name": "СУРСЫ ESENCE CLIENT",
        "files": [
            "cheats/3ssenc.zip",
        ],
    },
    "rockstar": {
        "name": "СУРСЫ ROCKSTAR CLIENT",
        "files": [
            "cheats/rockstar-client-src.rar",
        ],
    },
}
