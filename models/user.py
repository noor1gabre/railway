from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    whatsapp_number: Optional[str] = None
    password_hash: str
    role: str = Field(default="customer") # 'admin' or 'customer'