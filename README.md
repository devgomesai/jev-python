# JEV-PYTHON

<p align="center">
  <img src="img/jev-image.png" alt="JEV — Python wrapper for the Decisions API: noul (yes/no), choice (pick one), and score (rate 1–5) returning probabilities, options, and ratings" width="800" />
</p>

A Python sandbox for the [OpenRouter **Decisions** API](https://openrouter.ai/api/alpha/decisions) (`parallel/decisions-fast:free`).

Instead of free-form chat completions, the Decisions API answers **structured questions** about a `state` (some text you provide) and returns **typed, machine-readable answers** — probabilities, choices, and scores with confidence values. `jev.py` is a thin wrapper (`ask()`) around that endpoint; the numbered files are standalone examples, one per decision type.

## Decision types

All three decision types supported by the API are implemented:

| Type | What it answers | Answer shape | Example file |
|---|---|---|---|
| `noul` | Binary yes/no decision, returned as a probability (0–1) | `["is_refund"]["noul"]` → e.g. `0.94` | `01_test_call.py`, `03_noul.py` |
| `choice` | Picks ONE option from a list you define | `["team"]["choice"]` + `["confidence"]` | `02_choice.py` |
| `score` | Numeric rating on a scale you define (1–5) | `["candidate_score"]["score"]` + `["legend"]` + `["confidence"]` | `04_score.py` |

`05_example.py` combines all three types in one pipeline — see below.

### 1. `noul` — yes/no probabilistic decision
Ask whether something is true, get back a probability, then branch on a threshold (`> 0.5` → refund team, else → normal queue).
Used for: intent detection, gating, classification into exactly two buckets.

### 2. `choice` — single-select classification
Define the options and what each means in `criteria`; the API returns which option fits best plus a confidence.
Used for: routing (which support team?), category tagging, picking one of N known actions.

### 3. `score` — numeric rating with a legend
Define a scale and a rubric; the API returns a float score, a `legend` mapping each level to a label, and a confidence.
Used for: quality/fit ratings (candidate evaluation), prioritization, grading.

### 4. Putting it together — a full triage pipeline
`05_example.py` runs an 8-ticket support inbox through **five questions in a single `ask()` call** (two `noul` + one `choice` + two `score`) and turns the answers into an action:

- `noul` flags → urgent tickets (security/unauthorized payments) and refund-worthy tickets
- `choice` → routes to the right department (Technical Support / Billing / Account Management / Sales / Customer Success)
- `score` → business priority (1–5) and customer sentiment (1–5)
- Routing logic: low confidence (< 0.75) → human review, urgent → immediate notify, refund → refund queue, else → normal department queue

## Project structure

```
jev.py             # shared client: ask(state, questions) -> response["answers"]
01_test_call.py    # raw requests.post — noul type, inline (no jev.py import)
02_choice.py       # choice type — route 5 support messages to teams
03_noul.py         # noul type — refund detection over 8 messages
04_score.py        # score type — score 5 candidates for a Python backend role
05_example.py      # all 3 types combined — triage 8 support tickets (urgency, refund, department, priority, sentiment)
pyproject.toml     # uv project metadata + dependencies
tests/             # offline pytest suite (HTTP + sleep mocked, never contacts OpenRouter)
.env               # OPENROUTER_API_KEY + MODEL (not committed — see setup)
```

## Setup

Requirements: **Python 3.13+** and [uv](https://docs.astral.sh/uv/) (it can also install Python for you).

```powershell
# 1. Get an API key from https://openrouter.ai/keys  (must allow the free model)

# 2. Install dependencies (creates .venv automatically)
uv sync

# 3. Create a .env file in the project root:
#    OPENROUTER_API_KEY=sk-or-v1-...
#    MODEL=parallel/decisions-fast:free

# 4. Run the examples
uv run 01_test_call.py   # raw call + threshold routing
uv run 03_noul.py        # yes/no decisions
uv run 02_choice.py      # option picking / routing
uv run 04_score.py       # 1-5 scoring
uv run 05_example.py     # combined pipeline: full ticket triage
```

Or without installing uv: create a venv with Python 3.13+, `pip install python-dotenv requests`, and run `python 02_choice.py` etc. directly.

## How a question is structured

Every question is a dict entry — a name, a `type`, `instructions`, and `criteria` (modeled per type):

```python
question = {
    "team": {                                # your key for the answer
        "type": "choice",                    # noul | choice | score
        "instructions": "Which team should handle this message?",
        "criteria": {
            "shipping": "Deliveries, tracking, lost packages",
            "billing":  "Charges, refunds, invoices",
        },
    }
}

answers = ask(state="I was charged twice...", questions=question)
# answers["team"] -> choice, confidence
```

`criteria` changes shape per type: for `noul` it's `{"true": ..., "false": ...}`, for `choice` a `{option: description}` map, and for `score` a list of level descriptions (1 = first entry, 5 = last).

`state` accepts either a plain string or a dict (e.g. a structured ticket in `05_example.py`) — it is sent to the API unchanged.

## Environment, errors and retries

`ask()` reads `MODEL` and `OPENROUTER_API_KEY` from the environment on each call, so importing `jev.py` works without a configured `.env`; the error only surfaces when you call it (a descriptive `RuntimeError` naming the missing variable), or when the response has no `answers` key (alpha endpoint shape changes).

HTTP `429` and transient `5xx` (`500/502/503/504`) responses are retried up to **2 times** with exponential backoff (2s, then 4s); other `4xx` responses raise immediately via `requests.HTTPError`. The request timeout is 60 seconds.

## Tests

An offline pytest suite covers configuration errors, response handling, retry/backoff behavior and the exact request contract — all HTTP calls and sleeps are mocked, and the tests never contact OpenRouter or read real API keys:

```powershell
uv run pytest
```

## Notes

- [ ] The Decisions API is an **alpha** endpoint (`/api/alpha/decisions`) — response shape may change; `ask()` fails with a clear error if the `answers` key disappears.
- [ ] The free model (`parallel/decisions-fast:free`) has rate limits; transient `429`/`5xx` responses are retried automatically (2 retries, exponential backoff), but batch runs should still expect occasional failures.
- [ ] Make sure `.env` stays out of git and out of GitHub — rotate any key that was ever committed.
