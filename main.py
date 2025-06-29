from fastapi import FastAPI
from database import create_db_and_tables
from routers import tasks

app = FastAPI(title="Task Management API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {
        "message": "Welcome to the Task Management API",
        "endpoints": ["/health", "/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
