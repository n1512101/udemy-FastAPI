from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/user", tags=["user"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
  password: str
  new_password: str = Field(min_length=6)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication Failed")
  user_model = db.query(Users).filter(Users.id == user.get("id")).first()
  if user_model is None:
    raise HTTPException(status_code=404, detail="User not found.")
  return user_model

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication Failed")
  user_model = db.query(Users).filter(Users.id == user.get("id")).first()
  if user_model is None:
    raise HTTPException(status_code=404, detail="User not found.")
  if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
    raise HTTPException(status_code=401, detail="Error on password change")
  
  user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
  db.add(user_model)
  db.commit()

@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication Failed")
  user_model = db.query(Users).filter(Users.id == user.get("id")).first()
  user_model.phone_number = phone_number
  db.add(user_model)
  db.commit()