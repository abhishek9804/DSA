from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.tenants import router as tenant_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Entrprise Multi-Tenant RAG API",
)

app.include_router(health_router, prefix="/health")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tenant_router, prefix="/api/v1")

@app.get("/")
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "status": "running",
        "version": "0.2.0"
    }
