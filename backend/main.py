from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from datetime import datetime
from pathlib import Path

from database import get_db, engine
from models import Base, User, ChatSession, Message
from schemas import UserCreate, UserLogin, TokenResponse, MessageResponse, ChatSessionResponse
from auth import create_access_token, verify_token, get_password_hash, verify_password
from llm_service import process_chat_message
from file_handler import save_uploaded_image

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multimodal Chat API")

# Create uploads directory if it doesn't exist
Path("uploads").mkdir(parents=True, exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):

    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username
        }
    }

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }
    }

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@app.post("/api/chat/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    session = ChatSession(
        user_id=current_user.id,
        title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

@app.get("/api/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return sessions

@app.get("/api/chat/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific chat session"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    return messages

@app.post("/api/chat/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: int,
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message with optional image to a chat session"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Handle image upload
    image_path = None
    if image:
        image_path = await save_uploaded_image(image, current_user.id, session_id)
    
    # Save user message
    user_message = Message(
        session_id=session_id,
        role="user",
        content=text,
        image_path=image_path
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Get chat history for context
    previous_messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    
    # Process with LLM
    try:
        assistant_response = await process_chat_message(
            text=text,
            image_path=image_path,
            chat_history=previous_messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")
    
    # Save assistant message
    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=assistant_response
    )
    db.add(assistant_message)
    
    # Update session timestamp
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assistant_message)
    
    return assistant_message

@app.delete("/api/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)