from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# Import the core explanation function that handles all logic
from src.explain import explain 

app = FastAPI(title="Query-Driven Causal Explanation API")

# Define allowed origins for CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
     "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class Turn(BaseModel):
    turn_idx: int
    speaker: str
    time: str
    text: str

class QueryRequest(BaseModel):
    transcript: List[Turn]
    query: str
    top_k: int = 3

# --- Global Model Loading ---
MODEL_PATH = "models/causal-pair"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    MODEL_LOADED = True
    print(f"✅ Loaded tokenizer and model from {MODEL_PATH}")
except Exception as e:
    MODEL_LOADED = False
    tokenizer = None
    model = None
    print(f"FATAL ERROR: Could not load model. Requests will return an error. {e}")


# --- Consolidated Inference Runner (Cleaned up) ---
# This is where the old, faulty logic was. We now use the complete 'explain' function.
def run_inference(transcript_raw: List[Dict[str, Any]], query: str, top_k: int = 3):
    global tokenizer, model
    
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Causal model is not loaded or initialized.")

    # Calls the 'explain' function from src/explain.py
    explanation_result = explain(
        transcript=transcript_raw,
        query=query,
        tokenizer=tokenizer,
        model=model,
        top_k=top_k
    )
    
    return explanation_result


@app.post("/explain")
def explain_query(req: QueryRequest):
    transcript_raw = [t.dict() for t in req.transcript]

    try:
        explanation = run_inference(
            transcript_raw,
            req.query,
            req.top_k
        )
        return explanation
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error during explanation processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/")
def root():
    return {"message": "Causal Explanation API", "model_loaded": MODEL_LOADED, "docs": "/docs"}