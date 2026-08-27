"""Todo list API + 單頁前端。資料只存在記憶體（spec 規則 6）。"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, StrictBool

TITLE_MAX_LENGTH = 100
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Todo")


class TodoIn(BaseModel):
    title: str


class TodoPatch(BaseModel):
    done: StrictBool


class Todo(BaseModel):
    id: int
    title: str
    done: bool = False


class TodoStore:
    """記憶體儲存；id 從 1 開始遞增（規則 5）。"""

    def __init__(self) -> None:
        self._todos: list[Todo] = []
        self._next_id = 1

    def add(self, title: str) -> Todo:
        todo = Todo(id=self._next_id, title=title)
        self._next_id += 1
        self._todos.append(todo)
        return todo

    def list(self) -> list[Todo]:
        return list(self._todos)

    def update_done(self, todo_id: int, done: bool) -> Todo | None:
        for i, todo in enumerate(self._todos):
            if todo.id == todo_id:
                updated = todo.model_copy(update={"done": done})
                self._todos[i] = updated
                return updated
        return None


store = TodoStore()


def normalize_title(raw: str) -> str:
    """去頭尾空白並檢查長度（規則 2、3）。"""
    title = raw.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")
    if len(title) > TITLE_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"title must be at most {TITLE_MAX_LENGTH} characters",
        )
    return title


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/todos")
def list_todos() -> list[Todo]:
    return store.list()


@app.post("/api/todos", status_code=201)
def create_todo(body: TodoIn) -> Todo:
    return store.add(normalize_title(body.title))


@app.patch("/api/todos/{todo_id}")
def update_todo(todo_id: int, body: TodoPatch) -> Todo:
    todo = store.update_done(todo_id, body.done)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo
