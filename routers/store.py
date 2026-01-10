from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from db.database import get_session
from models.product import Product

router = APIRouter()

@router.get("/products", response_model=List[Product])
def get_all_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):
    return session.get(Product, product_id)