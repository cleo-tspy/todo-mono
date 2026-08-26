"""黑箱驗收測試：只透過 HTTP 與 app 互動，對應 spec.md 規則 1–6、8。"""

import pytest


def create(client, title):
    return client.post("/api/todos", json={"title": title})


# 規則 1
def test_post_returns_201_with_id_title_and_done_false(client):
    res = create(client, "buy milk")
    assert res.status_code == 201
    assert res.json() == {"id": 1, "title": "buy milk", "done": False}


# 規則 2
def test_post_strips_surrounding_whitespace(client):
    assert create(client, "  buy milk  ").json()["title"] == "buy milk"


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_post_blank_title_returns_400(client, title):
    assert create(client, title).status_code == 400


# 規則 3
def test_post_title_of_100_chars_is_accepted(client):
    assert create(client, "x" * 100).status_code == 201


def test_post_title_over_100_chars_returns_400(client):
    assert create(client, "x" * 101).status_code == 400


# 規則 4
def test_get_returns_todos_in_creation_order(client):
    for title in ["first", "second", "third"]:
        create(client, title)
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert [t["title"] for t in res.json()] == ["first", "second", "third"]


# 規則 5
def test_ids_start_at_1_and_increment(client):
    ids = [create(client, f"todo {n}").json()["id"] for n in range(3)]
    assert ids == [1, 2, 3]


# 規則 6
def test_fresh_server_starts_empty(client):
    assert client.get("/api/todos").json() == []


# 規則 8
def test_unknown_path_returns_404(client):
    assert client.get("/api/nope").status_code == 404


def test_malformed_json_returns_4xx_not_500(client):
    res = client.post(
        "/api/todos", content=b"{not json", headers={"Content-Type": "application/json"}
    )
    assert 400 <= res.status_code < 500


def test_missing_title_returns_4xx_not_500(client):
    res = client.post("/api/todos", json={"name": "oops"})
    assert 400 <= res.status_code < 500
