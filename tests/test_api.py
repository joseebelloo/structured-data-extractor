import json

import pytest
from fastapi.testclient import TestClient

from app import llm
from app.main import app

client = TestClient(app)

VALID_RESULT = {
    "title": "DataFlow Pro",
    "category": "ETL platform",
    "provider": "Acme Analytics",
    "price": "49 €/month",
    "summary": "Cloud ETL platform that connects data sources to your warehouse.",
}


def fake_llm(monkeypatch, responses):
    """Replace the real LLM with a fake that returns `responses` in order and records each call."""
    calls = []

    def fake_generate_json(prompt: str) -> str:
        calls.append(prompt)
        return responses[len(calls) - 1]

    monkeypatch.setattr(llm, "generate_json", fake_generate_json)
    return calls


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_success(monkeypatch):
    calls = fake_llm(monkeypatch, [json.dumps(VALID_RESULT)])

    response = client.post("/extract", json={"text": "DataFlow Pro by Acme Analytics, 49 €/month"})

    assert response.status_code == 200
    assert response.json() == VALID_RESULT
    assert len(calls) == 1


@pytest.mark.parametrize("body", [{"text": ""}, {"text": "   "}, {}, {"text": "x" * 10_001}])
def test_extract_invalid_input(monkeypatch, body):
    calls = fake_llm(monkeypatch, [])

    response = client.post("/extract", json=body)

    assert response.status_code == 422
    assert calls == []


def test_extract_retries_once_after_malformed_response(monkeypatch):
    calls = fake_llm(monkeypatch, ["this is not JSON", json.dumps(VALID_RESULT)])

    response = client.post("/extract", json={"text": "some text"})

    assert response.status_code == 200
    assert response.json() == VALID_RESULT
    assert len(calls) == 2


@pytest.mark.parametrize(
    "bad_response", ["this is not JSON", json.dumps({"title": "Only a title"})]
)
def test_extract_fails_after_two_bad_responses(monkeypatch, bad_response):
    calls = fake_llm(monkeypatch, [bad_response, bad_response])

    response = client.post("/extract", json={"text": "some text"})

    assert response.status_code == 502
    assert response.json() == {"detail": "The LLM returned an invalid response."}
    assert len(calls) == 2


def test_extract_llm_unavailable(monkeypatch):
    def broken_generate_json(prompt: str) -> str:
        raise ConnectionError("Gemini is down")

    monkeypatch.setattr(llm, "generate_json", broken_generate_json)

    response = client.post("/extract", json={"text": "some text"})

    assert response.status_code == 503
