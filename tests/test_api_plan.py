"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

PAYLOAD = {
    "destination": "Paris",
    "days": 3,
    "budget": 1500,
    "style": "city",
    "interests": ["museums", "food"],
}


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_destinations(client: TestClient) -> None:
    resp = client.get("/api/v1/destinations")
    assert resp.status_code == 200
    assert {"Paris", "Tokyo", "Bali"} <= set(resp.json()["destinations"])


def test_plan(client: TestClient) -> None:
    resp = client.post("/api/v1/plan", json=PAYLOAD)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["estimate"]["total"] == 663.0
    assert payload["estimate"]["within_budget"] is True
    assert len(payload["itinerary"]) == 3


def test_plan_rejects_too_many_days(client: TestClient) -> None:
    bad = dict(PAYLOAD, days=99)
    resp = client.post("/api/v1/plan", json=bad)
    assert resp.status_code == 422


def test_estimate(client: TestClient) -> None:
    resp = client.post("/api/v1/estimate", json=PAYLOAD)
    assert resp.status_code == 200
    assert resp.json()["total"] == 663.0


@pytest.mark.integration()
def test_relax_scenario_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: второй сценарий relax, без сети."""
    payload = dict(PAYLOAD, destination="Bali", days=2, style="relax", interests=[])
    resp = client.post("/api/v1/plan", json=payload)
    assert resp.status_code == 200
    assert "Swimwear" in resp.json()["packing"]
