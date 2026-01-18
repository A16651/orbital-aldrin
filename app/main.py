from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes import products, analysis

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend for Label Padhega India - Food Transparency App",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Label Padhega India Backend",
        "docs": "/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
