# =================================================
# admin_panel_streamlit.py
# =================================================

import streamlit as st
from pathlib import Path
import json

# ------------------------------
# Load & Save utilities
# ------------------------------
def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {item["tag"]: item["patterns"] for item in data}
            return data
    return {}

def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ------------------------------
# Admin Panel Class
# ------------------------------
class AdminPanel:
    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self.dataset = load_json(dataset_path)

    def add_intent(self, intent_name: str, patterns: list = None):
        if intent_name in self.dataset:
            if patterns:
                for p in patterns:
                    if p not in self.dataset[intent_name]:
                        self.dataset[intent_name].append(p)
        else:
            self.dataset[intent_name] = patterns or ["Example pattern"]
        save_json(self.dataset_path, self.dataset)

    def remove_intent(self, intent_name: str):
        if intent_name in self.dataset:
            del self.dataset[intent_name]
            save_json(self.dataset_path, self.dataset)

# ------------------------------
# Streamlit App
# ------------------------------
DATASET_PATH = Path(__file__).parent / "dataset.json"
admin = AdminPanel(DATASET_PATH)

st.title("📊 Chatbot Admin Panel")

# 1️⃣ Show current intents
st.subheader("Existing Intents")
if admin.dataset:
    for intent, patterns in admin.dataset.items():
        st.write(f"**{intent}** ({len(patterns)} patterns):")
        for p in patterns:
            st.write(f"- {p}")
else:
    st.write("No intents yet!")

st.markdown("---")

# 2️⃣ Add new intent
st.subheader("Add / Update Intent")
intent_name = st.text_input("Intent Name")
patterns_text = st.text_area("Patterns (one per line)")

if st.button("Add / Update Intent"):
    if intent_name.strip() == "" or patterns_text.strip() == "":
        st.warning("Please enter an intent name and at least one pattern.")
    else:
        patterns = [p.strip() for p in patterns_text.split("\n") if p.strip()]
        admin.add_intent(intent_name, patterns)
        st.success(f"Intent '{intent_name}' added/updated successfully!")
        st.experimental_rerun()  # refresh the page

st.markdown("---")

# 3️⃣ Remove intent
st.subheader("Remove Intent")
intent_to_remove = st.selectbox("Select Intent to Remove", list(admin.dataset.keys()) + [""])
if st.button("Remove Intent"):
    if intent_to_remove:
        admin.remove_intent(intent_to_remove)
        st.success(f"Intent '{intent_to_remove}' removed successfully!")
        st.experimental_rerun()
    else:
        st.warning("Please select an intent to remove.")