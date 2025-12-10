import google.generativeai as genai
from PIL import Image
import os
from typing import List, Optional
from models import Message
from dotenv import load_dotenv

load_dotenv() 

# Initialize Gemini client
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable must be set")

genai.configure(api_key=API_KEY)

# Configure model with settings
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

def load_image(image_path: str) -> Image.Image:

    return Image.open(image_path)

def build_message_history(chat_history: List[Message]) -> List[dict]:

    messages = []
    
    for msg in chat_history[:-1]:  # Exclude the most recent user message (will be added separately)
        # Map role: 'assistant' -> 'model' for Gemini
        role = "model" if msg.role == "assistant" else "user"
        
        parts = []
        
        # Add image if present
        if msg.image_path and os.path.exists(msg.image_path):
            try:
                image = load_image(msg.image_path)
                parts.append(image)
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Add text content
        parts.append(msg.content)
        
        messages.append({
            "role": role,
            "parts": parts
        })
    
    return messages

async def process_chat_message(
    text: str,
    image_path: Optional[str] = None,
    chat_history: List[Message] = None
) -> str:

    try:
        # Build message history
        history = build_message_history(chat_history) if chat_history else []
        
        # Build current message parts
        current_parts = []
        
        # Add image if present
        if image_path and os.path.exists(image_path):
            try:
                image = load_image(image_path)
                current_parts.append(image)
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Add text content
        current_parts.append(text)
        
        # Start chat with history
        chat = model.start_chat(history=history)
        
        # Send message
        response = chat.send_message(current_parts)
        
        # Extract text from response
        return response.text
    
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")