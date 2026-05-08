from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "ok", "message": "CogniAI service running"}


@app.get("/route")
def route_post(text: str = Query(..., description="Text to route to personas")):
    try:
        # Import lazily to avoid heavy imports at module import time
        from ai_cognitive_loop import route_post_to_bots

        bots = route_post_to_bots(text)
        return {"bots": bots}
    except Exception as exc:
        return {"error": str(exc)}
