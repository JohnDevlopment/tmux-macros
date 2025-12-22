#!/usr/bin/env bash

set -e

declare -r ROOTDIR=$(dirname $(realpath "$0"))

cd "$ROOTDIR"

source .venv/bin/activate

set +e

exec python macros.py "$@"
