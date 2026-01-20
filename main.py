# =================================================
# main.py
# =================================================

import sys
from pathlib import Path
import random
import json

# ------------------------------
# Add src root to path
# ------------------------------
SRC_ROOT = Path(__file__).resolve().parents[1]  # points to project root
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

# ------------------------------
# Imports
# ------------------------------
from intent_finetune.intent_classification import IntentClassifier
# from sentiment import main  # optional sentiment module

# ------------------------------
# Paths
# ------------------------------
CONVERSATION_STATE_PATH = SRC_ROOT / "src/intent_finetune/memory/conversation_state.json"
RESPONSES_PATH = SRC_ROOT / "src/intent_finetune/responses.json"

# ------------------------------
# Load conversation state safely
# ------------------------------
if CONVERSATION_STATE_PATH.exists() and CONVERSATION_STATE_PATH.stat().st_size > 0:
    with open(CONVERSATION_STATE_PATH, "r", encoding="utf-8") as f:
        conversation_state = json.load(f)
else:
    conversation_state = {}

# ------------------------------
# Load responses JSON
# ------------------------------
with open(RESPONSES_PATH, "r", encoding="utf-8") as f:
    responses = json.load(f)

# ------------------------------
# Chatbot class using IntentClassifier + memory
# ------------------------------
class Chatbot:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.conversation_state = conversation_state  # memory
        self.responses = responses

    def chatbot_reply(self, user_text, user_id="user1", confidence_threshold=0.6):
        # Initialize memory for user
        if user_id not in self.conversation_state:
            self.conversation_state[user_id] = {
                "history": [],
                "last_intent": None,
                "slots": {}
            }
        state = self.conversation_state[user_id]

        # ------------------------------
        # Predict intent
        # ------------------------------
        intent, confidence = self.classifier.predict_intent(user_text)

        # ------------------------------
        # Confidence handling
        # ------------------------------
        if confidence < confidence_threshold:
            response_text = "I'm not sure I understand. Can you clarify your issue?"
        else:
            # Optional sentiment handling
            # sentiment = main.get_sentiment(user_text)
            sentiment_prefix = ""
            # if sentiment == "negative":
            #     sentiment_prefix = "I understand this is frustrating. "

            # Context-aware response
            if state["last_intent"] == intent:
                response_text = sentiment_prefix + random.choice(self.responses[intent])
            else:
                response_text = sentiment_prefix + f"I see you have a {intent} issue. " + random.choice(self.responses[intent])

        # ------------------------------
        # Update memory
        # ------------------------------
        state["history"].append({"user": user_text, "intent": intent, "bot": response_text})
        state["last_intent"] = intent

        # Save conversation state
        with open(CONVERSATION_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.conversation_state, f, ensure_ascii=False, indent=4)

        return response_text

# ------------------------------
# TESTING
# ------------------------------
if __name__ == "__main__":
    bot = Chatbot()
    user_id = "user123"
    messages = [
        "My internet is very slow today",
        "It's not connecting at all now",
        "Also, I can't check my balance"
    ]

    for msg in messages:
        reply = bot.chatbot_reply(msg, user_id)
        print("User:", msg)
        print("Bot:", reply)
        print("-" * 50)