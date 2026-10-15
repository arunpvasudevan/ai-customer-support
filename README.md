AI Customer Support Assistant — Upgrade 2
A local learning project using Python, Ollama, Llama 3.2 1B, Streamlit, SQLite, and a keyword-based FAQ retriever.
Features
Generate a draft customer reply and troubleshooting steps.
Classify urgency, category, and sentiment.
Retrieve matching FAQ sections using basic keyword overlap (this is not vector search).
Save ticket history in SQLite.
Look up a saved ticket by ID through a controlled Python database tool.
Ask the local model to explain ticket facts returned by SQLite.
Manually update ticket status; the AI assistant cannot change it.
Dashboard charts, ticket history, review marking, filtering, and CSV export.
Automatically adds a `status` column to an older `tickets.db` when needed.
Runs locally; no OpenAI API key is required.
Requirements
Python 3.10 or newer
Ollama installed and running
`llama3.2:1b` model downloaded
Run on Windows
Open a terminal in the folder containing `web\_app.py`:
```powershell
ollama pull llama3.2:1b
python -m pip install -r requirements.txt
python -m streamlit run web\_app.py
```
Open the local URL printed by Streamlit, usually `http://localhost:8501`.
Try the new ticket lookup feature
Open Analyze issue and submit a fictional support issue.
Note the ticket ID shown after it is saved.
Open Ticket assistant and ask: `What is the status of ticket 1?` (replace `1` with the ID you received).
The app extracts the explicit ID, calls the Python `get\_ticket\_by\_id()` function, reads the matching row from SQLite, and passes those database facts to Ollama to phrase an answer.
The ticket assistant is read-only. Change status separately using the manual status control.
This is a controlled tool-integration step. The Python application decides which database function to call based on the explicit ticket ID; it is not yet autonomous model-selected tool calling.
Main files
`app.py`: Ollama request, response validation, FAQ retrieval, and ticket-answer phrasing.
`web\_app.py`: Streamlit interface, SQLite functions, ticket lookup tool, status management, analytics.
`knowledge\_base/support\_faq.txt`: fictional sample support guidance.
`tickets.db`: created automatically on first run; ignored by Git.
Safety and privacy
This is a portfolio/learning application, not a production support system. AI output may be inaccurate. Review all suggestions before use. Use fictional or anonymized data only. Do not enter customer secrets, passwords, tokens, or confidential HPE data. The code does not provide enterprise authentication, authorization, audit logging, or production security controls.