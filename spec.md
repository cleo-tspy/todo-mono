# Todo List 規格（黃金規格）

開發與驗證雙方都以本文件為準。實作：Python 3.12 + FastAPI，前端 vanilla JS，資料存記憶體。

## 基本規則（第 1 輪起生效）

1. `POST /api/todos`，body 為 JSON `{"title": "..."}` → 回 `201`，內容 `{"id": <int>, "title": "<str>", "done": false}`。
2. `title` 儲存前去除頭尾空白；去除後為空字串 → 回 `400`。
3. `title` 去除空白後超過 100 字 → 回 `400`。
4. `GET /api/todos` → 回 `200`，內容為陣列，依建立順序排列（先建立的在前）。
5. `id` 從 `1` 開始、每次加 `1`、不重複。
6. 資料只存在記憶體，伺服器重啟後清空。
7. `GET /` → 回 `200` 的 HTML 頁面，包含：文字輸入框（`id="title-input"`）、送出按鈕（`id="add-button"`）、清單（`id="todo-list"`）；頁面載入時顯示現有 todo，送出後清單立即新增，不重新整理頁面。
8. 不存在的路徑 → `404`；body 不是合法 JSON 或缺少 `title` → `4xx`；任何情況都不可回 `500`。

## 第 2 輪新增

9. `PATCH /api/todos/{id}`，body `{"done": true|false}` → 回 `200`，內容為更新後的物件；`id` 不存在 → `404`；body 缺少 `done` 或值不是布林 → `4xx`。
