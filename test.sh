#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x venv/bin/python ]; then
    echo "Сначала выполните ./install.sh"
    exit 1
fi
if ./venv/bin/python -m pytest -v; then
    echo "✅ Все тесты пройдены."
else
    result=$?
    echo "❌ Тестирование завершилось с ошибкой."
    exit "$result"
fi
