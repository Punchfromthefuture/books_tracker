#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d venv ]; then
    python3 -m venv venv
fi
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -c 'import db; db.init_db()'
echo "✅ Установка завершена. Запуск: ./run.sh; тесты: ./test.sh"
