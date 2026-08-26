#!/usr/bin/env bash
# 啟動 todo app：http://127.0.0.1:8000（Ctrl+C 結束）
cd "$(dirname "$0")"
uv run uvicorn main:app --port "${PORT:-8000}" --reload
