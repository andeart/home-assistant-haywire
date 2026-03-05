import asyncio
import json
import sys

import yaml

from ha_ws import connect


async def push_config(file_path, url_path):
    with open(file_path) as f:
        config = yaml.safe_load(f)

    async with connect() as ws:
        await ws.send(json.dumps({
            "id": 1,
            "type": "lovelace/config/save",
            "url_path": url_path,
            "config": config,
        }))
        result = json.loads(await ws.recv())
        if result.get("success"):
            print("Dashboard updated successfully.")
        else:
            print("Failed:", result)
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <path-to-yaml> <url_path>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(push_config(sys.argv[1], sys.argv[2]))
