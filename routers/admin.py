import uuid
import boto3
from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from core.security import get_password_hash
from schemas.product import ProductRead
from schemas.user import UserRead, UserUpdate
from sqlmodel import Session, select
from db.database import get_session
from models.product import Product
from models.user import User
from core.deps import get_current_admin
from core.config import R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_DOMAIN
import mimetypes
router = APIRouter()

s3_client = boto3.client(
    service_name='s3',
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto'
)
# 1. Update Product (تعديل منتج)
@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    name: str = Form(None),       # اختياري: لو مبعتش اسم مش هيتغير
    price: float = Form(None),
    category: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(None), # اختياري: لو مبعتش صورة هتفضل القديمة
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # تحديث البيانات النصية لو اتبعتت
    if name: product.name = name
    if price: product.price = price
    if category: product.category = category
    if description: product.description = description

    # تحديث الصورة لو اتبعتت صورة جديدة
    if file:
        try:
            file_ext = mimetypes.guess_extension(file.content_type) or ".bin"
            unique_name = f"{uuid.uuid4()}{file_ext}"
            content_type = file.content_type or "application/octet-stream"
            
            s3_client.upload_fileobj(
                file.file, R2_BUCKET_NAME, unique_name,
                ExtraArgs={'ContentType': content_type}
            )
            # تحديث الرابط في الداتابيز
            product.image_url = f"{R2_PUBLIC_DOMAIN}/{unique_name}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")

    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# 2. Delete Product (حذف منتج)
@router.delete("/products/{product_id}")
def delete_product(
    product_id: int, 
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(product)
    session.commit()
    return {"status": "deleted", "product_id": product_id}
@router.put("/settings", response_model=UserRead)
def update_admin_settings(
    settings: UserUpdate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin)
):
    # 1. لو بيحاول يغير الإيميل، نتأكد إنه مش محجوز لحد تاني
    if settings.email and settings.email != current_admin.email:
        existing_user = session.exec(select(User).where(User.email == settings.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_admin.email = settings.email

    # 2. تحديث باقي البيانات
    if settings.full_name:
        current_admin.full_name = settings.full_name
    
    if settings.whatsapp_number:
        current_admin.whatsapp_number = settings.whatsapp_number

    # 3. تحديث الباسورد لو موجود
    if settings.password:
        current_admin.password_hash = get_password_hash(settings.password)

    # 4. الحفظ في الداتابيز
    session.add(current_admin)
    session.commit()
    session.refresh(current_admin)
    
    return current_admin
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
        file_ext = mimetypes.guess_extension(file.content_type) or ".bin"
        unique_name = f"{uuid.uuid4()}{file_ext}"
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