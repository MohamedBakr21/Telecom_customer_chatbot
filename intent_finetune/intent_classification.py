# =================================================
# intent_classifier_predict.py
# =================================================

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pickle
from pathlib import Path
import json
import random
# =================================================
# CLASS DEFINITION
# =================================================
class IntentClassifier:
    def __init__(
        self,
        current_path: Path = None,
        model_path: Path = None,
        label_encoder_path: Path = None,
        responses_path: Path = None,
        num_labels: int = 8,
        device: str = None
    ):
        # ------------------------------
        # Default paths
        # ------------------------------
        if current_path is None:
            current_path = Path(__file__).parent.parent  # src/
        if model_path is None:
            model_path = current_path.parent / "models" / "intent_classifier_merged"
        if label_encoder_path is None:
            label_encoder_path = current_path / "intent_finetune" / "label_encoder.pkl"
        if responses_path is None:
            responses_path = current_path / "intent_finetune" / "responses.json"

        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.num_labels = num_labels

        # ------------------------------
        # Load tokenizer & model
        # ------------------------------
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            num_labels=self.num_labels,
            local_files_only=True
        ).to(self.device)
        self.model.eval()

        # ------------------------------
        # Load label encoder
        # ------------------------------
        with open(label_encoder_path, "rb") as f:
            self.label_encoder = pickle.load(f)

        # ------------------------------
        # Load responses
        # ------------------------------
        with open(responses_path, "r", encoding="utf-8") as f:
            self.responses = json.load(f)

    # =================================================
    # PREDICT INTENT ONLY
    # =================================================
    def predict_intent(self, user_text):
        """
        Returns: (intent_label:str, confidence:float)
        """
        inputs = self.tokenizer(user_text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
            pred_id = torch.argmax(probs, dim=-1).item()
            confidence = probs.max().item()
        intent = self.label_encoder.inverse_transform([pred_id])[0]
        return intent, confidence

    # =================================================
    # GET RESPONSE
    # =================================================
    def get_response(self, user_text, confidence_threshold=0.6):
        intent, confidence = self.predict_intent(user_text)
        if confidence < confidence_threshold:
            return "I'm not sure I understand. Can you clarify your issue?"
        return random.choice(self.responses[intent])


# =================================================
# TESTING
# =================================================
if __name__ == "__main__":
    classifier = IntentClassifier()

    test_texts = [
        "Why is my internet so slow today?",
        "I want to recharge my account",
        "How can I change my plan?"
    ]

    for text in test_texts:
        intent, confidence = classifier.predict_intent(text)
        response = classifier.get_response(text)
        print(f"Input: {text}")
        print(f"Predicted Intent: {intent}, Confidence: {confidence:.2f}")
        print(f"Response: {response}")
        print("-" * 50)