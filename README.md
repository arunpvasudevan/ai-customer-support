A beginner-friendly AI portfolio project built using Python, Ollama, Llama 3.2 1B, Streamlit, and SQLite.

Features

- AI-generated customer replies
- Troubleshooting recommendations
- Urgency classification: Low, Medium, or High
- Issue category classification
- Customer sentiment analysis
- Local SQLite ticket history
- Ticket analytics dashboard
- Search-like filtering by urgency, category, and review status
- Ticket review tracking
- CSV export
- Local AI inference without an OpenAI API key

Technologies

- Python
- Ollama
- Llama 3.2 1B
- Streamlit
- SQLite
- Pandas
- Requests
- Git and GitHub

Requirements

- Python 3.10 or newer
- Ollama installed and running
- The "llama3.2:1b" model downloaded

Installation

Install the Python dependencies:

python -m pip install -r requirements.txt

Download the AI model:

ollama pull llama3.2:1b

Start the web application:

python -m streamlit run web_app.py

Open the local URL displayed in the terminal, usually:

"http://localhost:8501"

Project files

- "app.py" — AI analysis logic and Ollama integration
- "web_app.py" — Streamlit user interface and ticket management
- "requirements.txt" — Python dependencies
- ".gitignore" — Files excluded from Git
- "tickets.db" — Local database created automatically

Responsible use

This is a learning project, not a production support system. AI responses can be inaccurate. A qualified person must review all suggestions before using them. Do not enter confidential customer information, passwords, or API keys.

The project does not replace enterprise security controls, incident management, or change approval procedures.