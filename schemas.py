from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime



class UserBase(BaseModel):
    username: str
    email: str
    password: str


class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_image: str | None = None
    model_config = ConfigDict(from_attributes=True)




class GroupCreate(BaseModel):
    name: str


class GroupResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    name: str
    email: Optional[str] = None


class ParticipantResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    paid_by_id: int  # participant id


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    paid_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BalanceResponse(BaseModel):
    participant_name: str
    balance: float

class TokenData(BaseModel):
    id: int
    username: str | None = None

class TokenIn(BaseModel):
    token: str

class Emails(BaseModel):
    email: str


class VerifyEmail(Emails):
    email: str
    verification_code: str
    model_config = ConfigDict(from_attributes=True)


class ResetPassword(BaseModel):
    email: str
    new_password: str