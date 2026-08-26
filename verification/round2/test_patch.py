"""第 2 輪新增：規則 9 PATCH /api/todos/{id}。第 2 輪開始時複製到 tests/。"""


def create(client, title="task"):
    return client.post("/api/todos", json={"title": title}).json()["id"]


def test_patch_marks_todo_done(client):
    todo_id = create(client)
    res = client.patch(f"/api/todos/{todo_id}", json={"done": True})
    assert res.status_code == 200
    assert res.json() == {"id": todo_id, "title": "task", "done": True}


def test_patch_can_mark_todo_not_done_again(client):
    todo_id = create(client)
    client.patch(f"/api/todos/{todo_id}", json={"done": True})
    assert client.patch(f"/api/todos/{todo_id}", json={"done": False}).json()["done"] is False


def test_patch_is_reflected_in_list(client):
    todo_id = create(client)
    client.patch(f"/api/todos/{todo_id}", json={"done": True})
    assert client.get("/api/todos").json()[0]["done"] is True


def test_patch_unknown_id_returns_404(client):
    assert client.patch("/api/todos/999", json={"done": True}).status_code == 404


def test_patch_without_boolean_done_returns_4xx(client):
    todo_id = create(client)
    assert 400 <= client.patch(f"/api/todos/{todo_id}", json={"done": "maybe"}).status_code < 500
    assert 400 <= client.patch(f"/api/todos/{todo_id}", json={}).status_code < 500
