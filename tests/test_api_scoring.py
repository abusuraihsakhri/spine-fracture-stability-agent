"""API smoke tests for score endpoints (legacy audit paths remain unchanged)."""
from fastapi.testclient import TestClient
from agents.api import app
from spine_fracture_stability_agent.server import create_app


def test_main_api_scores_tlics():
    response = TestClient(app).post("/api/score", json={
        "scale": "TLICS",
        "morphology": "burst",
        "ligament": "indeterminate",
        "neurologic": "intact",
    })
    assert response.status_code == 200
    assert response.json()["total"] == 4
    assert response.json()["band"] == "equivocal"


def test_main_api_rejects_incompatible_modifier():
    response = TestClient(app).post("/api/score", json={
        "scale": "SLIC",
        "morphology": "burst",
        "ligament": "intact",
        "neurologic": "intact",
        "ongoing_compression": True,
    })
    assert response.status_code == 422


def test_alternate_api_scores_slic():
    alt_app = create_app()
    assert alt_app is not None
    response = TestClient(alt_app).post("/api/score", json={
        "scale": "SLIC",
        "morphology": "distraction",
        "ligament": "disrupted",
        "neurologic": "incomplete_cord",
        "ongoing_compression": True,
    })
    assert response.status_code == 200
    assert response.json()["total"] == 9
