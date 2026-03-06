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

    try:
        async with websockets.connect(HA_WS_URL) as ws:
            await ws.recv()  # auth_required
            await ws.send(json.dumps({"type": "auth", "access_token": token}))
            auth_resp = json.loads(await ws.recv())
            if auth_resp.get("type") != "auth_ok":
                print("Auth failed:", auth_resp, file=sys.stderr)
                sys.exit(1)
            yield ws
    except OSError as e:
        print(f"Error: could not connect to {HA_WS_URL}: {e}", file=sys.stderr)
        if "HA_HOST" not in os.environ:
            print("Tip: set HA_HOST if mDNS doesn't work (e.g. export HA_HOST=192.168.1.x:8123)", file=sys.stderr)
        sys.exit(1)


class MessageSender:
    """Wraps an authenticated WS with auto-incrementing message IDs."""

    def __init__(self, ws):
        self._ws = ws
        self._id = 0

    async def call(self, msg_type, **kwargs):
        self._id += 1
        msg_id = self._id
        await self._ws.send(json.dumps({"id": msg_id, "type": msg_type, **kwargs}))
        while True:
            resp = json.loads(await self._ws.recv())
            if resp.get("id") == msg_id:
                break
        if not resp.get("success"):
            raise RuntimeError(f"WS call {msg_type} failed: {resp}")
        return resp.get("result")


@asynccontextmanager
async def connect_sender():
    async with connect() as ws:
        yield MessageSender(ws)
