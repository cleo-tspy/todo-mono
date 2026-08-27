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


def test_patch_updates_done_and_returns_updated_object(client):
    created = client.post("/api/todos", json={"title": "buy milk"}).json()
    res = client.patch(f"/api/todos/{created['id']}", json={"done": True})
    assert res.status_code == 200
    assert res.json() == {"id": created["id"], "title": "buy milk", "done": True}


def test_patch_can_set_done_back_to_false(client):
    created = client.post("/api/todos", json={"title": "buy milk"}).json()
    client.patch(f"/api/todos/{created['id']}", json={"done": True})
    res = client.patch(f"/api/todos/{created['id']}", json={"done": False})
    assert res.status_code == 200
    assert res.json()["done"] is False


def test_patch_nonexistent_id_returns_404(client):
    res = client.patch("/api/todos/999", json={"done": True})
    assert res.status_code == 404


@pytest.mark.parametrize("body", [{}, {"done": "true"}, {"done": 1}, {"done": None}, {"done": "yes"}])
def test_patch_missing_or_non_boolean_done_returns_4xx(client, body):
    created = client.post("/api/todos", json={"title": "buy milk"}).json()
    res = client.patch(f"/api/todos/{created['id']}", json=body)
    assert 400 <= res.status_code < 500


def test_patch_does_not_affect_other_todos(client):
    a = client.post("/api/todos", json={"title": "a"}).json()
    b = client.post("/api/todos", json={"title": "b"}).json()
    client.patch(f"/api/todos/{a['id']}", json={"done": True})
    res = client.get("/api/todos").json()
    assert res[0]["id"] == a["id"] and res[0]["done"] is True
    assert res[1]["id"] == b["id"] and res[1]["done"] is False
