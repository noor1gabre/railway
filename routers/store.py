from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from db.database import get_session
from models.product import Product
from schemas.product import ProductRead  

router = APIRouter()

@router.get("/products", response_model=List[ProductRead])
def get_all_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    return session.get(Product, product_id)