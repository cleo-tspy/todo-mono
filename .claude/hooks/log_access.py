#!/usr/bin/env python3
"""PreToolUse hook：記錄開發 agent 可能碰到 verification/ 的工具呼叫（只記錄、不阻擋）。

記錄兩種情況到 .claude/leak.log：
  hit      工具輸入明確提到 verification（讀檔、grep、cat、修改…）
  wide     Grep / Glob 沒指定 path 或指到專案根目錄（整個專案搜尋，結果會包含 verification/）
要改成硬性阻擋：把最後的 sys.exit(0) 改成 sys.exit(2)（stderr 內容會回傳給 agent）。
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

WATCHED = "verification"
WIDE_SEARCH_TOOLS = {"Grep", "Glob"}


def classify(tool_name, tool_input, project_dir):
    text = json.dumps(tool_input, ensure_ascii=False)
    if WATCHED in text:
        return "hit", text
    if tool_name in WIDE_SEARCH_TOOLS:
        path = tool_input.get("path")
        if not path or Path(path).resolve() == project_dir.resolve():
            return "wide", text
    return None, text


def main():
    payload = json.load(sys.stdin)
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    tool_name = payload.get("tool_name", "?")
    kind, text = classify(tool_name, payload.get("tool_input", {}), project_dir)
    if kind is None:
        sys.exit(0)
    log = project_dir / ".claude" / "leak.log"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%F %T}\t{kind}\t{tool_name}\t{text[:200]}\n")
    sys.exit(0)  # 改成 sys.exit(2) 即可阻擋


if __name__ == "__main__":
    main()
