from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel
from db.database import get_session
from models.user import User
from core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

@router.post("/signup")
def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Email exists")
    
    user = User(
        email=user_in.email, 
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
        role="customer" # Default
    )
    session.add(user)
    session.commit()
    return {"msg": "User created successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect login")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}