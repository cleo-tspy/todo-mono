"""規則 7：首頁存在且含必要元件（不跑瀏覽器，只檢查 HTML 內容）。"""


def test_index_page_has_input_button_and_list(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    for element_id in ("title-input", "add-button", "todo-list"):
        assert f'id="{element_id}"' in res.text


def test_index_page_uses_api_without_full_reload(client):
    html = client.get("/").text
    assert "/api/todos" in html
    assert "preventDefault" in html
