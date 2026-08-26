# 開發規範

- 需求以 `spec.md` 為準；程式碼在 `app/`，單元測試：`cd app && uv run pytest`。
- `verification/` 是驗證團隊的黑箱測試。**禁止讀取、搜尋、執行、修改該資料夾內任何檔案**（包含 cat / grep / ls / find 等指令，也不要執行 `verify.sh`）。驗收結果會由使用者轉告你。
- 完成後 commit 並 push 到 `main`。
