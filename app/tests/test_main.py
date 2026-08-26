"""開發側單元測試（白箱，直接載入 app）。"""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    main.store = main.TodoStore()
    return TestClient(main.app)


def test_create_returns_201_with_id_title_done(client):
    res = client.post("/api/todos", json={"title": "buy milk"})
    assert res.status_code == 201
    assert res.json() == {"id": 1, "title": "buy milk", "done": False}


def test_title_is_stripped(client):
    res = client.post("/api/todos", json={"title": "  hi  "})
    assert res.json()["title"] == "hi"


@pytest.mark.parametrize("title", ["", "   ", "x" * 101])
def test_invalid_title_returns_400(client, title):
    assert client.post("/api/todos", json={"title": title}).status_code == 400


def test_list_preserves_creation_order(client):
    for title in ["a", "b", "c"]:
        client.post("/api/todos", json={"title": title})
    assert [t["title"] for t in client.get("/api/todos").json()] == ["a", "b", "c"]


def test_index_serves_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert 'id="todo-list"' in res.text
