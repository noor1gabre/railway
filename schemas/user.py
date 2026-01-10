from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    whatsapp_number: Optional[str] = None # <-- عشان تظهر في البروفايل
    role: str
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    whatsapp_number: Optional[str] = None
    password: Optional[str] = None # اختياري: لو عايز يغير الباسورد كمان