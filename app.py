from fastapi import FastAPI, Request
from pydantic import BaseModel
from intent_finetune.intent_classification import IntentClassifier
import uvicorn
import random

# ------------------------------
# Initialize FastAPI and chatbot
# ------------------------------
app = FastAPI()
classifier = IntentClassifier()

# ------------------------------
# Request model
# ------------------------------
class UserMessage(BaseModel):
    user_id: str
    message: str

# ------------------------------
# Chatbot endpoint
# ------------------------------
@app.post("/chat")
async def chat_endpoint(msg: UserMessage):
    response = classifier.get_response(msg.message)
    return {"user_id": msg.user_id, "response": response}

# ------------------------------
# Optional root endpoint
# ------------------------------
@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}

# ------------------------------
# Run with: python app.py
# ------------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)