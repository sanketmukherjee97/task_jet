from fastapi import FastAPI

app = FastAPI(title="Task Jet", description="A simple task management API", version="1.0.0")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Task Jet API is running!"}