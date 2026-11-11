import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://openrouter.ai/api/alpha/decisions"
_TIMEOUT_SECONDS = 60
_RETRIES = 2          # retries after the initial attempt
_BACKOFF_SECONDS = 2  # wait before the first retry, doubled after each retry
_TRANSIENT_STATUSES = {429, 500, 502, 503, 504}


def _env(name: str) -> str:
    """Return a required environment variable, with a readable error if missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing configuration: {name} is not set. "
            f"Add {name}=... to your .env file in the project root (see README.md)."
        )
    return value


def _post_with_retries(headers: dict, payload: dict) -> requests.Response:
    """POST to the Decisions API, retrying 429 / transient 5xx up to _RETRIES times.

    Other statuses are returned untouched (``ask`` handles them via
    ``raise_for_status``), and unexpected exceptions or malformed responses
    are never retried.
    """
    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=_TIMEOUT_SECONDS,
    )
    for attempt in range(_RETRIES):
        if response.status_code not in _TRANSIENT_STATUSES:
            return response
        delay = _BACKOFF_SECONDS * 2**attempt
        print(f"Decisions API returned {response.status_code}, retrying in {delay}s ...")
        time.sleep(delay)
        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=_TIMEOUT_SECONDS,
        )
    return response


def ask(state: str | dict, questions: dict) -> dict:
    """Call the OpenRouter Decisions API and return its ``answers`` section.

    Args:
        state: The text (or dict, e.g. a structured ticket) the questions are
            evaluated against. Sent to the API unchanged.
        questions: Mapping of answer key to question definition, each with
            ``type`` (``noul`` | ``choice`` | ``score``), ``instructions``
            and ``criteria``.

    Returns:
        The ``answers`` dict from the API response, e.g.
        ``{"is_refund": {"noul": 0.94}}``.

    Raises:
        RuntimeError: If ``MODEL`` or ``OPENROUTER_API_KEY`` is not configured,
            or the response has no ``answers`` key.
        requests.HTTPError: On non-transient HTTP errors, or transient ones
            after all retries are exhausted.
    """
    response = _post_with_retries(
        headers={"Authorization": f"Bearer {_env('OPENROUTER_API_KEY')}"},
        payload={
            "model": _env("MODEL"),
            "state": state,
            "questions": questions,
        },
    )
    response.raise_for_status()
    data = response.json()
    if "answers" not in data:
        raise RuntimeError(f"Unexpected API response: no 'answers' key. Got keys: {list(data)}")
    # print(json.dumps(data, indent=2)) # Uncomment to inspect the full response payload.
    return data["answers"]
