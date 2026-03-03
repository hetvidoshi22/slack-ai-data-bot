# Slack AI Data Bot

A Slack AI application that converts natural language questions into SQL using **LangChain**, executes them on **Postgres**, and returns formatted results directly in Slack.

---

## 🚀 What This Project Does

- Accepts natural language queries via `/ask-data`
- Uses LangChain (LLM) to convert NL → SQL
- Executes SQL on Postgres (`sales_daily` table)
- Returns compact, formatted results in Slack
- Handles execution errors safely
- Implements caching to optimize repeated queries

---

## 🧠 Architecture

```mermaid
flowchart LR
    A[Slack Slash Command] --> B[FastAPI Backend]
    B --> C[LangChain + LLM]
    C --> D[Generated SQL]
    D --> E[PostgreSQL Database]
    E --> B
    B --> A

---

## ⚙️ Tech Stack 

- Python
- FastAPI
- LangChain (ChatGroq)
- PostgreSQL
- Slack Slash Commands
- ngrok (local tunneling)

---

## 📊 Database Schema

CREATE TABLE public.sales_daily (
    date date NOT NULL,
    region text NOT NULL,
    category text NOT NULL,
    revenue numeric(12,2) NOT NULL,
    orders integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (date, region, category)
);

---

## 💬 Example Queries

/ask-data show revenue by region for 2025-09-01
/ask-data show total revenue for 2025-09-02
/ask-data how much did we earn on 2025-09-02?
/ask-data show revenue by category

---

## ✅ Key Features

- Deterministic SQL generation (temperature = 0)
- Prompt-constrained SELECT-only output
- Automatic SQL cleanup (removes markdown, prefixes)
- Compact Slack formatting (business readable)
- Graceful error handling (no crashes / no timeouts)
- In-memory caching for repeated queries 

---

## 🎥 Demo Video

Google Drive Demo Link: [Paste Your Video Link Here]

---

## ▶️ Run Locally
1. Set environment variables:
   - `GROQ_API_KEY`
   - `DATABASE_URL`
   - `SLACK_BOT_TOKEN`

2. Start server: uvicorn app:app --port 8000


3. Expose with ngrok: ngrok http 8000


4. Set Slack Request URL to: https://<ngrok-url>/slack/ask-data


