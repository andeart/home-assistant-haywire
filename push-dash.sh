#!/bin/bash

# USAGE
# ./push-dash.sh my-dashboard-slug

if [ -z "$1" ]; then
    echo "Usage: $0 <url_path>" >&2
    exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install websockets
pip install pyyaml

if ! yamllint -d "{extends: relaxed, rules: {line-length: disable}}" "temp/${1}.yaml"; then
    echo "YAML lint failed. Aborting push." >&2
    exit 1
fi

python3 utils/util_push_dash.py "temp/${1}.yaml" "$1"
echo "Pushed temp/${1}.yaml back to HA."