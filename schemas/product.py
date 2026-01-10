from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    price: float
    description: str | None = None
    category: str = "General"

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    image_url: str | None = None

    class Config:
        from_attributes = True 