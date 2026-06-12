from pydantic import BaseModel
from typing import List, Optional

class EvalItem(BaseModel):
    id: str
    prompt: str
    reference_answer: str
    model_answer: str

class EvalRequest(BaseModel):
    items: List[EvalItem]

class ItemResult(BaseModel):
    id: str
    score: float
    reason: str

class Summary(BaseModel):
    average_score: float
    num_items: int
    num_exact_matches: int
    num_failed_items: int

class EvalResponse(BaseModel):
    results: List[ItemResult]
    summary: Summary
    
