import asyncio
import sys

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


def compute_diff(current_items, desired_items):
    """Compare current (from HA) vs desired (from YAML) for one helper type.

    Returns (to_create, to_update) where:
      to_create: list of config dicts (without 'id')
      to_update: list of (id, full_config_dict)
    """
    current_by_id = {item["id"]: item for item in current_items}
    desired_by_id = {item["id"]: item for item in desired_items}

    current_ids = set(current_by_id)
    desired_ids = set(desired_by_id)

    to_create = []
    for did in sorted(desired_ids - current_ids):
        config = {k: v for k, v in desired_by_id[did].items() if k != "id"}
        to_create.append(config)

    to_update = []
    for eid in sorted(current_ids & desired_ids):
        current_config = current_by_id[eid]
        desired_config = desired_by_id[eid]
        all_keys = set(current_config) | set(desired_config)
        all_keys.discard("id")
        if any(current_config.get(k) != desired_config.get(k) for k in all_keys):
            full_update = {k: v for k, v in desired_config.items() if k != "id"}
            to_update.append((eid, full_update))

    return to_create, to_update


def print_plan(plan):
    """Print a human-readable summary of planned changes. Returns True if any."""
    has_changes = False
    for helper_type, (creates, updates) in plan.items():
        if not creates and not updates:
            continue
        has_changes = True
        print(f"\n  {helper_type}:")
        for config in creates:
            print(f"    + CREATE: {config.get('name', '(unnamed)')}")
        for eid, _ in updates:
            print(f"    ~ UPDATE: {eid}")
    return has_changes


async def push_helpers(yaml_path, auto_confirm=False):
    with open(yaml_path) as f:
        desired = yaml.safe_load(f) or {}

    async with connect_sender() as sender:
        # Pull current state and compute diff
        plan = {}
        for helper_type in HELPER_TYPES:
            current_items = await sender.call(f"{helper_type}/list")
            desired_items = desired.get(helper_type, [])
            plan[helper_type] = compute_diff(current_items, desired_items)

        # Print plan and confirm
        print("Planned changes:")
        if not print_plan(plan):
            print("  No changes detected.")
            return

        if not auto_confirm:
            answer = input("\nApply these changes? [y/N] ")
            if answer.lower() not in ("y", "yes"):
                print("Aborted.")
                sys.exit(0)

        # Apply changes
        ok, fail = 0, 0
        for helper_type, (creates, updates) in plan.items():
            id_key = f"{helper_type}_id"

            for config in creates:
                try:
                    await sender.call(f"{helper_type}/create", **config)
                    print(f"  Created {helper_type}: {config.get('name')}")
                    ok += 1
                except RuntimeError as e:
                    print(f"  FAILED create {helper_type} {config.get('name')}: {e}", file=sys.stderr)
                    fail += 1

            for eid, fields in updates:
                try:
                    await sender.call(f"{helper_type}/update", **{id_key: eid, **fields})
                    print(f"  Updated {helper_type}: {eid}")
                    ok += 1
                except RuntimeError as e:
                    print(f"  FAILED update {helper_type} {eid}: {e}", file=sys.stderr)
                    fail += 1

        print(f"\nDone: {ok} succeeded, {fail} failed.")
        if fail:
            sys.exit(1)


if __name__ == "__main__":
    auto = "--yes" in sys.argv or "-y" in sys.argv
    path = next((a for a in sys.argv[1:] if not a.startswith("-")), "temp/helpers.yaml")
    asyncio.run(push_helpers(path, auto_confirm=auto))
