"""黑箱測試共用設定：每個測試都重新啟動一個乾淨的 app 程序（規則 6）。

APP_DIR 環境變數指向受測 app 的資料夾（內含 main.py 與 pyproject.toml）。
"""

import os
import socket
import subprocess
import time
from pathlib import Path

import httpx
import pytest

STARTUP_TIMEOUT_SECONDS = 20


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_ready(base_url: str, process: subprocess.Popen, log_path: Path) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"app 啟動失敗（exit {process.returncode}）：\n{log_path.read_text()}")
        try:
            httpx.get(f"{base_url}/api/todos", timeout=0.5)
            return
        except httpx.HTTPError:
            time.sleep(0.1)
    raise RuntimeError(f"app 在 {STARTUP_TIMEOUT_SECONDS}s 內沒有啟動：\n{log_path.read_text()}")


def _stop(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture
def base_url(tmp_path: Path) -> str:
    app_dir = Path(os.environ.get("APP_DIR", "")).resolve()
    if not (app_dir / "main.py").exists():
        pytest.fail(f"APP_DIR 未指向 app 資料夾：{app_dir}")
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    log_path = tmp_path / "app.log"
    with log_path.open("w") as log:
        process = subprocess.Popen(
            ["uv", "run", "uvicorn", "main:app", "--port", str(port), "--log-level", "warning"],
            cwd=app_dir,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    try:
        _wait_until_ready(url, process, log_path)
        yield url
    finally:
        _stop(process)


@pytest.fixture
def client(base_url: str) -> httpx.Client:
    with httpx.Client(base_url=base_url, timeout=5) as client:
        yield client
