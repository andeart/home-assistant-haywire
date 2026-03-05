#!/bin/bash
set -euo pipefail

# USAGE
# ./pull-dash.sh my-dashboard-slug

if [ -z "$1" ]; then
    echo "Usage: $0 <url_path>" >&2
    exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install websockets

python3 utils/util_pull_dash.py "$1" | jq '.result' | yq -P > "temp/${1}.yaml"
echo "Saved file to temp/${1}.yaml"
open "temp/${1}.yaml"