from fastapi import FastAPI
from models import EvalRequest, EvalResponse, ItemResult, Summary
from scorer import score_answer

app = FastAPI(
    title="AI Answer Evaluator",
    description="Scores model answers against reference answers deterministically.",
    version="1.0.0"
)

@app.post("/evaluate", response_model=EvalResponse)
def evaluate(request: EvalRequest):
    """
    Evaluate a list of prompt/answer pairs.
    Returns per-item scores and an overall summary.
    """
    results = []
    total_score = 0.0
    exact_matches = 0
    failed_items = 0

    for item in request.items:
        score, reason = score_answer(item.reference_answer, item.model_answer)

        if score == 1.0:
            exact_matches += 1
        if score == 0.0:
            failed_items += 1

        total_score += score
        results.append(ItemResult(id=item.id, score=score, reason=reason))

    num_items = len(results)
    average_score = round(total_score / num_items, 4) if num_items > 0 else 0.0

    summary = Summary(
        average_score=average_score,
        num_items=num_items,
        num_exact_matches=exact_matches,
        num_failed_items=failed_items
    )

    return EvalResponse(results=results, summary=summary)

@app.get("/health")
def health():
    return {"status": "ok"}
    