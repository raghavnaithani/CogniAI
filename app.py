from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Mount static files at /static and serve the SPA at root
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_index():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(index_path)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "CogniAI service running"}


@app.get("/route")
def route_post(text: str = Query(..., description="Text to route to personas")):
    try:
        # Import lazily to avoid heavy imports at module import time
        from ai_cognitive_loop import route_post_to_bots, rank_post_to_bots

        bots = route_post_to_bots(text)
        ranked = rank_post_to_bots(text)
        return {
            "bots": bots,
            "ranked": ranked,
            "message": "No exact match above threshold" if not bots else "Matched bots found",
        }
    except Exception as exc:
        return {"error": str(exc)}
