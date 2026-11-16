#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x venv/bin/python ]; then
    echo "Сначала выполните ./install.sh"
    exit 1
fi
exec ./venv/bin/python main.py
