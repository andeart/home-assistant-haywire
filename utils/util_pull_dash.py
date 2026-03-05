import asyncio
import json
import sys

from ha_ws import connect


async def pull_config(url_path):
    async with connect() as ws:
        await ws.send(json.dumps({"id": 1, "type": "lovelace/config", "url_path": url_path}))
        result = await ws.recv()
        print(result)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url_path>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(pull_config(sys.argv[1]))
