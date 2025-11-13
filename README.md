# 🎯 Query-driven Causal Explanation System

This project implements a **Query-driven Causal Explanation Interface** that identifies *why* something happened in a conversation or transcript.  
Given a **query** (e.g., “Why was the release delayed?”) and a **dialogue transcript**, the system generates **a human-understandable explanation** supported by evidence from the dialogue.

It combines **Natural Language Processing (NLP)**, **context-aware reasoning**, and an **interactive UI** to visualize cause–effect explanations.

---

## 🧩 Project Structure

mockps/
├── backend/
│ ├── app.py # FastAPI backend
│ ├── requirements.txt # Python dependencies
│ ├── explanation_model.py # Core explanation generation logic
│ └── ...
├── frontend/
│ ├── src/
│ │ └── App.jsx # React frontend logic
│ │ └── index.css
│ ├── package.json
│ └── ...
└── README.md

##How It Works

1.User Input: You enter a query and a conversation transcript.

2.Backend Processing:

Extracts causal relationships between statements.

Identifies key claims and supporting evidence using semantic similarity & reasoning models.

3. Frontend Display:

Shows a clear explanation followed by evidence for each claim.

Clicking evidence highlights the corresponding line in the transcript.


##Why This Solution? (Justification & Knowledge)

Most existing dialogue analysis tools either:

Only summarize conversations, or

Only extract entities and sentiments.

However, causal reasoning — understanding why something happened — is crucial for decision making (e.g., in project reviews, customer calls, or medical discussions).

Our solution:

Implements a transparent explainability pipeline.

Gives both claim (main reason) and evidence (supporting context).

Uses NLP-based semantic matching and sentence embeddings (e.g., SBERT or DistilBERT) to connect causes and effects.

Presents results in an interactive, human-readable interface.

This makes it ideal for:

Root-cause analysis

Meeting analysis

Explanation generation for conversational AI


---

## ⚙️ **Installation & Execution Steps**

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/mockps.git
cd mockps
cd backend
python -m venv venv
venv\Scripts\activate      # (Windows)
# OR
source venv/bin/activate   # (Linux/Mac)

Install dependencies
pip install -r requirements.txt
Run backend server
uvicorn app:app --reload
Set up frontend
cd ../frontend
npm install
npm run dev
'''




