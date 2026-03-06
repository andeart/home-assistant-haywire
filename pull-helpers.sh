#!/bin/bash
set -euo pipefail

# USAGE
# ./pull-helpers.sh

[[ -d .venv ]] || python3 -m venv .venv
source .venv/bin/activate
pip install -q --disable-pip-version-check -r utils/requirements.txt

mkdir -p temp
python3 utils/util_pull_helpers.py > temp/helpers.yaml
echo "Saved helpers to temp/helpers.yaml"
open temp/helpers.yaml
