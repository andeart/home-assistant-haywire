#!/bin/bash
set -euo pipefail

# USAGE
# ./push-helpers.sh          # interactive confirmation
# ./push-helpers.sh --yes    # skip confirmation

[[ -d .venv ]] || python3 -m venv .venv
source .venv/bin/activate
pip install -q --disable-pip-version-check -r utils/requirements.txt

if ! yamllint -d "{extends: relaxed, rules: {line-length: disable}}" temp/helpers.yaml; then
    echo "YAML lint failed. Aborting push." >&2
    exit 1
fi

python3 utils/util_push_helpers.py temp/helpers.yaml "$@"
