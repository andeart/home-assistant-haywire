import asyncio
import json
import os
import sys

import websockets

async def get_config(url_path):
    async with websockets.connect("ws://homeassistant.local:8123/api/websocket") as ws:
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": os.environ["HA_UI_EDIT_TOKEN"]}))
        await ws.recv()  # auth_ok
        await ws.send(json.dumps({"id": 1, "type": "lovelace/config", "url_path": url_path}))
        result = await ws.recv()
        print(result)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url_path>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(get_config(sys.argv[1]))