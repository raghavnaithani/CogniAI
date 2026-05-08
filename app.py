from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files at /static and serve the SPA at root.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

BOT_PERSONAS = {
    "bot_a": {
        "keywords": {"ai", "crypto", "bitcoin", "elon", "space", "technology", "openai"},
    },
    "bot_b": {
        "keywords": {"privacy", "nature", "monopoly", "billionaire", "critical", "social", "capitalism"},
    },
    "bot_c": {
        "keywords": {"markets", "interest", "rates", "trading", "roi", "finance", "stocks"},
    },
}


def _score_persona(text: str, keywords: set[str]) -> int:
    lower_text = text.lower()
    return sum(1 for keyword in keywords if keyword in lower_text)


def _rank_bots(text: str) -> list[dict]:
    ranked = []
    for bot_id, persona in BOT_PERSONAS.items():
        raw_score = _score_persona(text, persona["keywords"])
        score = raw_score / max(1, len(persona["keywords"]))
        ranked.append(
            {
                "bot_id": bot_id,
                "score": score,
                "persona": bot_id,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


@app.get("/")
def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "CogniAI service running"}


@app.get("/route")
def route_post(text: str = Query(..., description="Text to route to personas")):
    ranked = _rank_bots(text)
    bots = [item["bot_id"] for item in ranked if item["score"] >= 0.3]
    return {
        "bots": bots,
        "ranked": ranked,
        "message": "No exact match above threshold" if not bots else "Matched bots found",
    }
