#!/usr/bin/env bash
# 對指定 app 跑黑箱驗收測試。用法：./run.sh [APP_DIR]（預設 ../app）
set -euo pipefail
cd "$(dirname "$0")"
export APP_DIR="${1:-$(pwd)/../app}"
uv run pytest -q -rf
