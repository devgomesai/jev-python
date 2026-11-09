"""Offline tests for jev.py and script import-safety.

Every HTTP call and every sleep is mocked — the suite never contacts OpenRouter
and never needs a real .env (required env vars are injected/deleted per test).
"""

import importlib
import sys

import pytest
import requests

import jev


class FakeResponse:
    """Minimal stand-in for requests.Response (offline only)."""

    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"answers": {}}

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


@pytest.fixture
def configured_env(monkeypatch):
    monkeypatch.setenv("MODEL", "test/model:free")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")


@pytest.fixture
def no_env(monkeypatch):
    monkeypatch.delenv("MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)


def install(monkeypatch, responses):
    """Route requests.post through canned FakeResponses and stub time.sleep.

    Returns (calls, sleeps): recorded request kwargs and backoff delays.
    """
    calls, sleeps = [], []
    index = {"i": 0}

    def fake_post(url, headers=None, json=None, timeout=None):
        response = responses[min(index["i"], len(responses) - 1)]
        index["i"] += 1
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return response

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(jev.time, "sleep", sleeps.append)
    return calls, sleeps


# --- configuration -----------------------------------------------------------


@pytest.mark.parametrize("name", ["MODEL", "OPENROUTER_API_KEY"])
def test_missing_env_raises_descriptive_error(no_env, monkeypatch, name):
    other = "OPENROUTER_API_KEY" if name == "MODEL" else "MODEL"
    monkeypatch.setenv(other, "test-value")
    with pytest.raises(RuntimeError, match=name):
        jev.ask("state", {})


def test_import_does_not_require_env(no_env):
    # jev must be importable without .env; the error only appears when ask() runs.
    assert isinstance(jev.URL, str)


# --- happy path --------------------------------------------------------------


def test_successful_response_returns_answers(configured_env, monkeypatch):
    calls, sleeps = install(monkeypatch, [FakeResponse(200, {"answers": {"is_refund": {"noul": 0.94}}})])
    answers = jev.ask("hello", {"is_refund": {"type": "noul"}})
    assert answers == {"is_refund": {"noul": 0.94}}
    assert len(calls) == 1
    assert sleeps == []


def test_missing_answers_key_raises_without_retry(configured_env, monkeypatch):
    calls, sleeps = install(monkeypatch, [FakeResponse(200, {"unexpected": "shape"})])
    with pytest.raises(RuntimeError, match="answers"):
        jev.ask("hello", {})
    assert len(calls) == 1
    assert sleeps == []


# --- HTTP error handling -----------------------------------------------------


@pytest.mark.parametrize("status_code", [400, 401, 403, 404])
def test_other_4xx_fails_without_retry(configured_env, monkeypatch, status_code):
    calls, sleeps = install(monkeypatch, [FakeResponse(status_code)])
    with pytest.raises(requests.HTTPError):
        jev.ask("hello", {})
    assert len(calls) == 1
    assert sleeps == []


def test_429_retries_then_succeeds(configured_env, monkeypatch):
    calls, sleeps = install(
        monkeypatch,
        [FakeResponse(429), FakeResponse(429), FakeResponse(200, {"answers": {"ok": 1}})],
    )
    assert jev.ask("hello", {}) == {"ok": 1}
    assert len(calls) == 3  # initial + 2 retries
    assert sleeps == [2, 4]  # exponential backoff


def test_429_retries_exhausted(configured_env, monkeypatch):
    calls, sleeps = install(monkeypatch, [FakeResponse(429)])
    with pytest.raises(requests.HTTPError):
        jev.ask("hello", {})
    assert len(calls) == 3
    assert sleeps == [2, 4]


def test_5xx_retries_then_succeeds(configured_env, monkeypatch):
    calls, _ = install(monkeypatch, [FakeResponse(500), FakeResponse(503), FakeResponse(200, {"answers": {}})])
    assert jev.ask("hello", {}) == {}
    assert len(calls) == 3


def test_5xx_retries_exhausted(configured_env, monkeypatch):
    calls, sleeps = install(monkeypatch, [FakeResponse(500)])
    with pytest.raises(requests.HTTPError):
        jev.ask("hello", {})
    assert len(calls) == 3
    assert sleeps == [2, 4]


# --- request contract (endpoint / payload unchanged) -------------------------


def test_request_url_headers_payload_and_timeout(configured_env, monkeypatch):
    calls, _ = install(monkeypatch, [FakeResponse(200, {"answers": {}})])
    questions = {"team": {"type": "choice", "instructions": "pick", "criteria": {"a": "x"}}}
    jev.ask("I was charged twice", questions)
    call = calls[0]
    assert call["url"] == "https://openrouter.ai/api/alpha/decisions"
    assert call["headers"] == {"Authorization": "Bearer test-key"}
    assert call["json"] == {
        "model": "test/model:free",
        "state": "I was charged twice",
        "questions": questions,
    }
    assert call["timeout"] == 60


# --- import-safety of the numbered example scripts ---------------------------


@pytest.mark.parametrize(
    "script",
    ["01_test_call", "02_choice", "03_noul", "04_score", "05_example"],
)
def test_importing_example_script_makes_no_api_call(monkeypatch, no_env, script):
    def forbidden_post(*args, **kwargs):
        raise AssertionError("requests.post must not be called by importing an example")

    monkeypatch.setattr(requests, "post", forbidden_post)
    sys.modules.pop(script, None)
    try:
        importlib.import_module(script)
    finally:
        sys.modules.pop(script, None)
