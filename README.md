# AI Answer Evaluator
### Deriv AI Engineer Assessment — Build-and-Break Challenge

---

## What This Project Does

This is a lightweight REST API service that evaluates AI model answers against reference answers using deterministic scoring rules. It was built as part of the Deriv AI Engineer hands-on assessment.

**Real-world use case:** Before releasing an AI-powered feature, a team needs to test whether the model is producing high-quality responses. This tool lets you feed in a batch of prompts with expected answers, score what the model actually said, and get a structured report back — without relying on another LLM to judge the output.

---

## Project Structure

```
deriv-assessment/
├── main.py           # FastAPI app — defines the API endpoint
├── scorer.py         # Scoring logic — isolated and independently testable
├── models.py         # Pydantic schemas — defines input/output data shapes
├── test_scorer.py    # Unit tests for the scoring logic
└── README.md         # This file
```

### Why this structure?

Each file has a single responsibility. The scoring logic in `scorer.py` has zero dependency on the web framework — meaning another engineer can swap FastAPI for Flask, or turn this into a CLI tool, without touching the core logic. This is intentional design for extensibility.

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip

### Step 1 — Clone the repo
```bash
git clone https://github.com/CalvinChin2310/Deriv.git
cd Deriv
```

### Step 2 — Install dependencies
```bash
pip install fastapi uvicorn
```

### Step 3 — Start the server
```bash
python -m uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## Using The API

### Option 1 — Swagger UI (Recommended for demo)

Open your browser and go to:
```
http://localhost:8000/docs
```

This gives you a full interactive UI to test the API — no extra tools needed.

### Option 2 — curl

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "id": "1",
        "prompt": "What is 2 + 2?",
        "reference_answer": "4",
        "model_answer": "The answer is 4."
      },
      {
        "id": "2",
        "prompt": "Name one primary color.",
        "reference_answer": "red",
        "model_answer": "blue"
      },
      {
        "id": "3",
        "prompt": "What planet do humans live on?",
        "reference_answer": "Earth",
        "model_answer": "Humans live on Earth."
      },
      {
        "id": "4",
        "prompt": "Reply with exactly: approved",
        "reference_answer": "approved",
        "model_answer": "Approved"
      }
    ]
  }'
```

### Expected Response

```json
{
  "results": [
    {
      "id": "1",
      "score": 0.775,
      "reason": "Partial match — 1/1 reference tokens found. Containment: 1.00, Jaccard: 0.25"
    },
    {
      "id": "2",
      "score": 0.0,
      "reason": "Partial match — 0/1 reference tokens found. Containment: 0.00, Jaccard: 0.00"
    },
    {
      "id": "3",
      "score": 0.775,
      "reason": "Partial match — 1/1 reference tokens found. Containment: 1.00, Jaccard: 0.25"
    },
    {
      "id": "4",
      "score": 1.0,
      "reason": "Exact match after normalization"
    }
  ],
  "summary": {
    "average_score": 0.6375,
    "num_items": 4,
    "num_exact_matches": 1,
    "num_failed_items": 1
  }
}
```

---

## API Reference

### `POST /evaluate`

Accepts a list of evaluation items and returns per-item scores plus an overall summary.

**Request body:**
```json
{
  "items": [
    {
      "id": "string",
      "prompt": "string",
      "reference_answer": "string",
      "model_answer": "string"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "string",
      "score": 0.0,
      "reason": "string"
    }
  ],
  "summary": {
    "average_score": 0.0,
    "num_items": 0,
    "num_exact_matches": 0,
    "num_failed_items": 0
  }
}
```

### `GET /health`

Returns service health status.

```json
{ "status": "ok" }
```

---

## Scoring Logic — How It Works

### Step 1 — Normalize
Both answers are lowercased and whitespace is trimmed before any comparison.
```
"  Earth  " → "earth"
"Approved" → "approved"
```

### Step 2 — Exact Match Check
If the normalized answers are identical, score is `1.0` immediately.

### Step 3 — Token Overlap (Partial Score)
If not exact, the text is tokenized using regex (`\b\w+\b`) which strips punctuation automatically. This means `"4."` and `"4"` correctly match.

Two metrics are computed and blended:

| Metric | Weight | Purpose |
|---|---|---|
| **Containment** | 70% | Did the model answer contain all reference tokens? Rewards correct but verbose answers like `"The answer is 4"` |
| **Jaccard** | 30% | How much do both token sets overlap overall? Penalises answers that include the reference but add a lot of noise |

**Formula:**
```
final_score = (0.7 × containment) + (0.3 × jaccard)
```

### Step 4 — Edge Cases
| Situation | Score | Reason |
|---|---|---|
| Model answer is empty or missing | `0.0` | Failed item |
| Reference answer is empty or missing | `0.0` | Failed item |
| Genuinely wrong answer (no token overlap) | `0.0` | No match |

---

## Running The Tests

```bash
python test_scorer.py
```

Expected output:
```
✅ test_exact_match passed: score=1.0
✅ test_case_insensitive passed: score=1.0
✅ test_partial_match passed: score=0.775
✅ test_wrong_answer passed: score=0.0
✅ test_missing_answer passed: score=0.0
✅ test_normalize passed

✅ All tests passed.
```

### What Each Test Covers

| Test | What It Verifies |
|---|---|
| `test_exact_match` | Same answer scores 1.0 |
| `test_case_insensitive_exact_match` | `"Approved"` vs `"approved"` scores 1.0 after normalization |
| `test_partial_match` | Verbose but correct answer scores between 0 and 1 |
| `test_wrong_answer` | Completely wrong answer scores 0.0 |
| `test_missing_model_answer` | Empty model answer scores 0.0 with clear reason |
| `test_normalize` | Normalization strips whitespace and lowercases correctly |

---

## Tradeoffs & Design Decisions

### What I chose and why

**FastAPI over CLI** — A REST service is more extensible. A CLI is a dead end; a service can be called by a pipeline, a CI job, a frontend dashboard, or another microservice with zero code changes.

**Deterministic scoring over LLM-as-judge** — The problem explicitly said no external API calls. But even beyond that, deterministic scoring is auditable, reproducible, and fast. LLM-as-judge is powerful but non-deterministic and expensive at scale.

**Containment + Jaccard blend over pure Jaccard** — Pure Jaccard unfairly penalises model answers that are correct but verbose (a very common LLM pattern). Containment alone rewards any answer that includes the reference word even buried in junk. The blend gives a fairer result for realistic model outputs.

**Separated scorer.py from main.py** — The scoring logic has no dependency on FastAPI. It can be imported, tested, or reused in any context. This separation makes the codebase easier to maintain and extend.

---

## Next Improvements (If Given More Time)

1. **Semantic scoring** — Add optional embedding-based similarity using `sentence-transformers` for cases where meaning matters more than exact tokens (e.g. `"Earth"` vs `"our planet"`)
2. **Configurable scoring weights** — Let callers pass custom weights for containment vs Jaccard per evaluation job
3. **Async batch processing** — For large eval sets (1000+ items), switch to async endpoints with background task queuing
4. **Scoring profiles** — Define named profiles like `strict` (exact match only) or `semantic` (embedding-based) selectable per request
5. **Persistent storage** — Log evaluation runs to PostgreSQL so teams can track model quality over time
6. **Auth + rate limiting** — Add API key auth and rate limiting before any production deployment
7. **CI integration** — Add GitHub Actions to run tests automatically on every push

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| FastAPI | REST API framework |
| Pydantic | Input/output validation and schema definition |
| Uvicorn | ASGI server |
| re (stdlib) | Regex-based tokenization |

No external LLM APIs used. Fully local and runnable offline.
