# updated app.py
#python -m uvicorn app:app --reload
from fastapi import FastAPI
from pydantic import BaseModel
from model import generate_story
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Urdu Story Generator")

# CORS configuration
origins = [
    "http://localhost:3000",                  # local dev
    "https://your-vercel-frontend.vercel.app", # production
    "https://nlp-a1-production.up.railway.app" # your railway backend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------
# Request format
# -------------------------
class GenerateRequest(BaseModel):
    prefix: str = ""
    max_sentences: int = 5  # Adjustable number of sentences

# -------------------------
# Response format
# -------------------------
class GenerateResponse(BaseModel):
    story: str

# -------------------------
# Root endpoint - Fixes the 404 at base URL
# -------------------------
@app.get("/")
def root():
    return {
        "message": "Urdu Story Generator API",
        "version": "1.0",
        "endpoints": {
            "generate": "/generate (POST) - Generate a story",
            "docs": "/docs (GET) - Interactive API documentation",
            "redoc": "/redoc (GET) - Alternative documentation",
            "health": "/health (GET) - Health check"
        }
    }

# -------------------------
# Health check endpoint
# -------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Urdu Story Generator",
        "generate_endpoint": "/generate"
    }

# -------------------------
# Main API endpoint
# -------------------------
@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        story = generate_story(prefix=req.prefix, max_sentences=req.max_sentences)
        return {"story": story}
    except Exception as e:
        # Return error as story for now (you might want better error handling)
        return {"story": f"Error generating story: {str(e)}"}