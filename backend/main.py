from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3


app = FastAPI(title="Finance Analyzer")


# Allow our frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE = "finance.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


create_table()


class Transaction(BaseModel):
    amount: float
    type: str
    category: str
    description: str = ""
    date: str


@app.get("/")
def home():
    return {"message": "Finance Analyzer API is running"}


@app.post("/transactions")
def create_transaction(transaction: Transaction):

    if transaction.type not in ["income", "expense"]:
        raise HTTPException(
            detail="Type must be income or expense"
        )

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO transactions
        (amount, type, category, description, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            transaction.amount,
            transaction.type,
            transaction.category,
            transaction.description,
            transaction.date
        )
    )

    connection.commit()

    transaction_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Transaction created successfully",
        "id": transaction_id
    }


@app.get("/transactions")
def get_transactions():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM transactions
        ORDER BY date DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):

    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM transactions
        WHERE id = ?
        """,
        (transaction_id,)
    )

    connection.commit()

    connection.close()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {
        "message": "Transaction deleted successfully"
    }


@app.get("/analytics")
def get_analytics():

    connection = get_connection()

    income = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'income'
        """
    ).fetchone()[0]

    expenses = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense'
        """
    ).fetchone()[0]

    connection.close()

    savings = income - expenses

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings
    }