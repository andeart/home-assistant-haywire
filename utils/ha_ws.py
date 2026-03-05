import json
import os
import sys
from contextlib import asynccontextmanager

import websockets

HA_HOST = os.environ.get("HA_HOST", "homeassistant.local:8123")
HA_WS_URL = f"ws://{HA_HOST}/api/websocket"


@asynccontextmanager
async def connect():
    token = os.environ.get("HA_UI_EDIT_TOKEN")
    if not token:
        print("Error: HA_UI_EDIT_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    async with websockets.connect(HA_WS_URL) as ws:
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        auth_resp = json.loads(await ws.recv())
        if auth_resp.get("type") != "auth_ok":
            print("Auth failed:", auth_resp, file=sys.stderr)
            sys.exit(1)
        yield ws
