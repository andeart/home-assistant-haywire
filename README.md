# HA Dashboard Configuration Editor

CLI tooling for round-tripping Home Assistant Lovelace dashboard configs via the WebSocket API. Pull, edit locally, lint, and push back, all without a server restart.

## Why?

HA stores managed (UI-mode) Lovelace dashboards in `.storage/lovelace.*` as JSON. Editing these files directly requires a full server restart for HA to invalidate its memory cache and reload them. HA may also flush its in-memory state back to disk on restart, overwriting our edits entirely. YAML-mode dashboards don't have this problem, of course, but we lose the visual editor there.

The WebSocket API sidesteps this entirely. `lovelace/config` reads the live config, `lovelace/config/save` writes it back. Changes take effect immediately without a restart. The shell scripts abstract away that round-trip.

Note: The `yamllint` in `push-dash` isn't optional. HA's WS API will silently accept malformed config and leave our dashboard in a broken state. The lint catches that before it hits the server. That said, back up your dashboard data before pushing with this tool.

## Requirements

- **HA access token**: Generate a long-lived token from your HA instance under **Profile > Security > Long-Lived Access Tokens**. Export it to env vars as `HA_UI_EDIT_TOKEN`.
- **WebSocket endpoint**: The scripts default to `ws://homeassistant.local:8123` (mDNS). If your setup doesn't resolve `.local`, swap in your IP and port directly in the shell scripts.

## Usage

```bash
# Pull a dashboard by its URL path
./pull-dash.sh my-dashboard-slug
# saves to temp/my-dashboard-slug.yaml and opens the file for editing

# Push edits back
./push-dash.sh my-dashboard-slug
# runs yamllint, then pushes temp/my-dashboard-slug.yaml to HA
```

## Dependencies

- `jq` and `yq`: used in the pull pipeline to extract and reshape the nested JSON config payload into YAML
- `yamllint`: validates the edited YAML before push to prevent silent dashboard corruption
- `python3` with `pip`: runtime for the WebSocket scripts

The shell scripts automatically create a `.venv` and install the required pip packages:

- `websockets`: for the HA WebSocket API client
- `pyyaml`: for YAML serialization during the config round-trip
