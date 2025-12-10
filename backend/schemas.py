from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ChatSessionCreate(BaseModel):
    title: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    text: str
    image: Optional[str] = None  # base64 encoded image

class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    image_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True