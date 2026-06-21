from fastapi import FastAPI

app = FastAPI(title="Task Jet", description="A simple task management API", version="1.0.0")

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Task Jet API is running!"}