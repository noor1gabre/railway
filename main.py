import os
import sys
import uuid
import boto3
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ==========================================
# 1. Cloudflare R2 Configuration ☁️
# ==========================================
# حط البيانات اللي اشتغلت معاك في ملف الاختبار هنا
# --- بياناتك ---
ACCOUNT_ID = "1fc8fb2e1a931161faa604bb1dbab8b7"
ACCESS_KEY = "73a823150346bdf1946e7b6a4f6a9aac"
SECRET_KEY = "7fff51048bbeb44c91a373ff1ccb546ed3ca4f5558d1412ea9e02cb128ce6719"
BUCKET_NAME = "products"  # اسم البوكيت بتاعك
R2_PUBLIC_DOMAIN="https://pub-9d8e69f9b5e6474d90bccbed1591bca8.r2.dev"

# Initialize S3 Client
s3_client = boto3.client(
    service_name='s3',
    endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=ACCOUNT_ID,
    aws_secret_access_key=SECRET_KEY,
)

# ==========================================
# 2. Database Configuration 🗄️
# ==========================================
db_url = os.environ.get("DATABASE_URL")

# إصلاح مشكلة postgres:// لو موجودة
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url:
    print("⚠️ WARNING: DATABASE_URL not found. DB operations might fail.")

# إنشاء الاتصال
engine = create_engine(db_url) if db_url else None

# تعريف جدول المنتجات
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None # ضفتلك حقل للصورة عشان تربط الاثنين ببعض

# ==========================================
# 3. App Setup & CORS ⚙️
# ==========================================
app = FastAPI()

# السماح للـ Frontend يكلم الـ Backend (مهم جداً لصاحبك)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج يفضل نحدد دومين الفرونت بس
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    if engine:
        SQLModel.metadata.create_all(engine)

# ==========================================
# 4. Endpoints 🚀
# ==========================================

@app.get("/")
def home():
    return {"status": "Online", "message": "E-commerce API is running 🚀"}

# --- Endpoint 1: Upload Image to R2 ---
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 1. Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # 2. Upload to Cloudflare R2
        s3_client.upload_fileobj(
            file.file, 
            BUCKET_NAME, 
            unique_filename,
            ExtraArgs={'ContentType': file.content_type} 
        )
        
        # 3. Construct URL
        image_url = f"{R2_PUBLIC_DOMAIN}/{unique_filename}"
        
        return {"status": "success", "url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint 2: Create Product (Save to DB) ---
@app.post("/products/", response_model=Product)
def create_product(product: Product):
    if not engine:
        raise HTTPException(status_code=500, detail="Database not connected")
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

# --- Endpoint 3: List All Products ---
@app.get("/products/", response_model=List[Product])
def read_products():
    if not engine:
        return []
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products