import asyncio

import yaml

from ha_ws import connect_sender

HELPER_TYPES = [
    "input_boolean",
    "input_number",
    "input_select",
    "input_text",
    "input_datetime",
    "input_button",
    "counter",
    "timer",
    "schedule",
]


async def pull_helpers():
    async with connect_sender() as sender:
        result = {}
        for helper_type in HELPER_TYPES:
            items = await sender.call(f"{helper_type}/list")
            if items:
                result[helper_type] = items

    print(yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True), end="")


if __name__ == "__main__":
    asyncio.run(pull_helpers())
