import uuid
import boto3
from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from schemas.product import ProductRead
from sqlmodel import Session
from db.database import get_session
from models.product import Product
from models.user import User
from core.deps import get_current_admin
from core.config import R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_DOMAIN

router = APIRouter()

s3_client = boto3.client(
    service_name='s3',
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto'
)

@router.post("/products", response_model=ProductRead)
def create_product(
    name: str = Form(...), 
    price: float = Form(...), 
    category: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    try:
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        content_type = file.content_type or "application/octet-stream"
        
        s3_client.upload_fileobj(
            file.file, R2_BUCKET_NAME, unique_name,
            ExtraArgs={'ContentType': content_type}
        )
        image_url = f"{R2_PUBLIC_DOMAIN}/{unique_name}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")

    product = Product(
        name=name, price=price, description=description, 
        category=category, image_url=image_url
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product