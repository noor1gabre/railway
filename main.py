from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Active", "message": "Hello from Railway! 🚀"}

@app.get("/test")
def test():
    return {"data": "System is working fine."}