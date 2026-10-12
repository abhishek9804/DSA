from fastapi import FastAPI
from app.api.health import router

app = FastAPI(
    title="Enterprise Multi Tenant RAG"
)

app.include_router(
    router,
    prefix="/health"
)

@app.get("/")
def home():

    return {
        "status": "running"
    }
