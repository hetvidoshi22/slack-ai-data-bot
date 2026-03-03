# Simple in-memory cache
query_cache = {}

import os
import psycopg2
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

load_dotenv()

app = FastAPI()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0
)
DATABASE_URL = os.getenv("DATABASE_URL")


def clean_sql(output: str):
    output = output.strip()

    if "```" in output:
        output = output.split("```")[1]

    output = output.replace("sql", "")
    return output.strip()


def generate_sql(question: str):
    prompt = f"""
You are a PostgreSQL expert.

The database has one table:

Table: public.sales_daily

Columns:
- date (date, format YYYY-MM-DD)
- region (text: North, South, East, West)
- category (text: Electronics, Grocery, Fashion)
- revenue (numeric)
- orders (integer)
- created_at (timestamptz)

Interpret natural language questions and convert them into ONE valid PostgreSQL SELECT statement.

Rules:
- Use SUM(revenue) when the question asks about earnings, revenue, income, sales, or total revenue.
- Use SUM(orders) when the question asks about total orders.
- Filter by region when the user mentions north, south, east, or west.
- Filter by date when a date is mentioned.
- Use correct format: 'YYYY-MM-DD'
- Return ONLY the SQL query.
- Do NOT explain anything.
- Do NOT include markdown.
- Only return one SELECT statement.

Question: {question}
"""

    response = llm.invoke(prompt)
    return clean_sql(response.content)

def execute_sql(query: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return colnames, rows


@app.post("/slack/ask-data")
async def ask_data(request: Request):
    form = await request.form()
    user_question = form.get("text")

    try:
        # Check cache first
        if user_question in query_cache:
            cached_response = query_cache[user_question]
            print("⚡ Cache hit")
            return cached_response

        # Generate SQL
        sql_query = generate_sql(user_question)
        print("Generated SQL:", sql_query)

        # Execute query
        columns, rows = execute_sql(sql_query)

        if not rows:
            response = {
                "response_type": "ephemeral",
                "text": "No data found."
            }
            query_cache[user_question] = response
            return response

        # Format results
        preview_lines = []

        for row in rows[:5]:
            formatted_values = []

            for value in row:
                if hasattr(value, "as_tuple"):
                    value = float(value)

                if isinstance(value, float):
                    value = f"{value:.2f}"

                formatted_values.append(str(value))

            if len(formatted_values) == 2:
                line = f"{formatted_values[0]} → {formatted_values[1]}"
            else:
                line = " | ".join(formatted_values)

            preview_lines.append(line)

        preview = "\n".join(preview_lines)

        response = {
            "response_type": "in_channel",
            "text": f"*Query:*\n```{sql_query}```\n\n*Results:*\n```{preview}```"
        }

        # Store in cache
        query_cache[user_question] = response

        return response

    except Exception as e:
        error_response = {
            "response_type": "ephemeral",
            "text": f"```{str(e)}```"
        }
        return error_response