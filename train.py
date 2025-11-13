import json
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
# Import the necessary metrics from scikit-learn
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Model and output directory
MODEL_NAME = "distilbert-base-uncased"
OUT_DIR = "models/causal-pair"

# ----------------------------
# Load dataset safely (No change needed here)
# ----------------------------
pairs = []
data_path = "data/pairs.jsonl"

with open(data_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # skip empty lines
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"⚠️ Skipping invalid JSON line: {line[:80]}...")
            continue

        # Make sure expected keys exist
        if all(k in obj for k in ["query", "candidate_text", "label"]):
            pairs.append({
                "query": obj["query"],
                "candidate": obj["candidate_text"],
                "label": int(obj["label"])
            })
        else:
            print(f"⚠️ Skipping line missing keys: {line[:80]}")

# Convert list to Hugging Face Dataset
ds = Dataset.from_list(pairs)
ds = ds.train_test_split(test_size=0.2, seed=42)

# ----------------------------
# Tokenizer and model (No change needed here)
# ----------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

def preprocess_function(examples):
    return tokenizer(
        examples["query"],
        examples["candidate"],
        truncation=True,
        padding="max_length",
        # 🔑 CHANGE 1: Increase max_length to accommodate conversational context
        max_length=512 
    )

tokenized = ds.map(preprocess_function, batched=True)
tokenized = tokenized.rename_column("label", "labels")
tokenized.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# ----------------------------
# Training setup (No change needed here)
# ----------------------------
training_args = TrainingArguments(
    output_dir=OUT_DIR,
    eval_strategy="epoch",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    save_total_limit=1,
    learning_rate=2e-5,
    logging_dir=f"{OUT_DIR}/logs",
    logging_strategy="epoch"
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    
    # 🔑 CHANGE 2: Add Precision, Recall, and F1-score
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='binary', pos_label=1, zero_division=0
    )
    acc = accuracy_score(labels, preds)
    
    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

# ----------------------------
# Trainer (No change needed here)
# ----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# ----------------------------
# Train and save (No change needed here)
# ----------------------------
trainer.train()
trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)

print(f"✅ Training complete. Model saved to: {OUT_DIR}")