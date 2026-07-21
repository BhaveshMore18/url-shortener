from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_shorten_url():
    response = client.post("/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com"

def test_redirect(monkeypatch):
    create_response = client.post("/shorten", json={"original_url": "https://example.com"})
    short_code = create_response.json()["short_code"]
    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code in (302, 307)


def test_cache_hit_on_redirect():
    create_response = client.post("/shorten", json={"original_url": "https://example.com"})
    short_code = create_response.json()["short_code"]

    # First redirect - cache miss, populates cache
    client.get(f"/{short_code}", follow_redirects=False)
    # Second redirect - should now be a cache hit
    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code in (302, 307)

def test_stats_endpoint():
    create_response = client.post("/shorten", json={"original_url": "https://example.com"})
    short_code = create_response.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)
    response = client.get(f"/stats/{short_code}")
    assert response.status_code == 200
    assert response.json()["clicks"] >= 1

def test_stats_not_found():
    response = client.get("/stats/nonexistent")
    assert response.status_code == 404