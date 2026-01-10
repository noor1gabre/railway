from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import create_db_and_tables
from routers import auth, admin, store

app = FastAPI(title="Family & Home API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ربط الراوترات
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin Control"])
app.include_router(store.router, prefix="/api/v1/store", tags=["Storefront"])

@app.get("/")
def home():
    return {"status": "Online", "message": "API V1 is Running 🚀"}