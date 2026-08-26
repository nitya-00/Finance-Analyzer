from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Transaction
from pydantic import BaseModel , Field
from fastapi import HTTPException



# PHASE 1 REFERENCE — SQLITE + RAW SQL

# Frontend
#     ↓
# FastAPI
#     ↓
# sqlite3
#     ↓
# finance.db
#
# SQLite stores the entire database inside one file:
#
#     finance.db

# import sqlite3
#
#
# DATABASE = "finance.db"
#
#
# # Creates a connection between Python and the SQLite database.





# def get_connection():
#
#     connection = sqlite3.connect(DATABASE)
#
#     # This allows us to access columns using their names.
#     # Example:
#     # row["amount"]
#     #
#     # instead of:
#     # row[1]
#     connection.row_factory = sqlite3.Row
#
#     return connection
#
#
# # Creates the transactions table if it doesn't already exist.



# def create_table():
#
#     connection = get_connection()
#
#     connection.execute("""
#         CREATE TABLE IF NOT EXISTS transactions (
#
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#
#             amount REAL NOT NULL,
#
#             type TEXT NOT NULL,
#
#             category TEXT NOT NULL,
#
#             description TEXT,
#
#             date TEXT NOT NULL
#         )
#     """)
#
#     # Save the database changes.
#     connection.commit()
#
#     # Close the connection after we're finished.
#     connection.close()
#
#
# # Create the table when the application starts.
# create_table()


# PHASE 2 — SQLALCHEMY + POSTGRESQL

#
# Our new architecture:
#
# Frontend
#     ↓
# FastAPI
#     ↓
# SQLAlchemy
#     ↓
# PostgreSQL
#
# SQLAlchemy is the Python layer that helps our application
# communicate with the PostgreSQL database.
#
# We are using an ORM (Object Relational Mapper).
#
# Instead of manually writing SQL like:
#
#     SELECT * FROM transactions;
#
# we can write Python/SQLAlchemy code such as:
#
#     db.query(Transaction).all()
#
# SQLAlchemy converts our Python instructions into SQL.
# ============================================================


# Create our FastAPI application.
#
# This "app" object is the main application that Uvicorn runs.
app = FastAPI(
    title="Finance Analyzer"
)
#
# Our frontend and backend are running on different ports.
#
# Frontend:
#     http://127.0.0.1:5500
#
# Backend:
#     http://127.0.0.1:8000
#
# Because they are different origins, the browser needs
# permission to allow the frontend to communicate with
# the backend.
#
# CORS = Cross-Origin Resource Sharing
# ============================================================
class TransactionCreate(BaseModel):

    # Amount must be greater than 0.
    amount: float = Field(gt=0)

    type: str
    category: str
    description: str = ""

    date: str


    
app.add_middleware(
    CORSMiddleware,

    # Which frontend URLs are allowed to communicate
    # with our backend.
    #
    # "*" means allow all origins.
    #
    # This is convenient for development.
    # Later, in production, we should restrict this
    # to our actual frontend domain.
    allow_origins=["*"],

    # Allow cookies/credentials when required.
    allow_credentials=True,

    # Allow GET, POST, PUT, DELETE, etc.
    allow_methods=["*"],

    # Allow headers such as Content-Type and Authorization.
    allow_headers=["*"],
)


# ============================================================
# DATABASE TABLE CREATION
# ============================================================
#
# "Base" comes from database.py.
#
# Base is the parent class for our SQLAlchemy models.
#
# For example:
#
#     class Transaction(Base):
#
# Because Transaction inherits from Base, SQLAlchemy knows
# that Transaction represents a database table.
#
# Base.metadata contains information about all the tables
# that SQLAlchemy knows about.
#
# create_all() means:
#
#     "Look at all my models and create their tables
#      in the database if they don't already exist."
#
# bind=engine tells SQLAlchemy:
#
#     "Use THIS database connection/engine."
#
# So:
#
#     Base.metadata.create_all(bind=engine)
#
# means:
#
#     Models
#       ↓
#     Base.metadata
#       ↓
#     create tables
#       ↓
#     engine
#       ↓
#     PostgreSQL
#
# IMPORTANT:
# create_all() does NOT mean "delete everything and recreate it".
# It creates tables that don't already exist.
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# HOME ENDPOINT
# ============================================================
#
# @app.get("/")
#
# This tells FastAPI:
#
#     When someone sends a GET request to "/",
#     execute the function immediately below it.
#
# Example:
#
#     Browser
#        ↓
#     GET http://127.0.0.1:8000/
#        ↓
#     home()
#
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Personal Finance Analyzer API is running"
    }


# ============================================================
# GET ALL TRANSACTIONS
# ============================================================
#
# This endpoint gets all transactions from PostgreSQL.
#
# Frontend:
#
#     fetch("http://127.0.0.1:8000/transactions")
#
#        ↓
#
#     GET /transactions
#
#        ↓
#
#     FastAPI calls get_transactions()
#
#        ↓
#
#     SQLAlchemy gets the data
#
#        ↓
#
#     PostgreSQL
#
# ============================================================

@app.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # What is "Session"?
    # --------------------------------------------------------
    #
    # Session comes from:
    #
    #     from sqlalchemy.orm import Session
    #
    # A Session represents a temporary conversation with
    # the database.
    #
    # We use the session to:
    #
    #     - query data
    #     - add data
    #     - update data
    #     - delete data
    #     - commit changes
    #
    # --------------------------------------------------------
    #
    # What is "get_db"?
    # --------------------------------------------------------
    #
    # get_db comes from database.py:
    #
    #     def get_db():
    #
    #         db = SessionLocal()
    #
    #         try:
    #             yield db
    #
    #         finally:
    #             db.close()
    #
    # SessionLocal creates a database Session.
    #
    # get_db gives that session to our API endpoint.
    #
    # --------------------------------------------------------
    #
    # What does Depends(get_db) mean?
    # --------------------------------------------------------
    #
    # Depends() is FastAPI's dependency injection system.
    #
    # It basically tells FastAPI:
    #
    #     "Before running this function, run get_db()
    #      and give me the database session."
    #
    # Therefore:
    #
    #     db
    #
    # is the database session we will use below.
    #
    # --------------------------------------------------------

    transactions = (
        db.query(Transaction)

        # Sort transactions by date.
        #
        # desc() = descending order
        #
        # So newest transactions appear first.
        .order_by(
            Transaction.date.desc()
        )

        # Actually execute the query and return all rows.
        .all()
    )

    return transactions

@app.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    # Find one transaction using its ID.
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    # If no transaction exists with this ID,
    # return a 404 error.
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction


@app.post("/transactions")
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):

    # Make sure the transaction type is valid.
    if transaction.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be income or expense"
        )

    # Create a SQLAlchemy Transaction object.
    #
    # This does NOT insert it into PostgreSQL yet.
    #
    # We are simply creating a Python object
    # that represents a database row.

    new_transaction = Transaction(
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        description=transaction.description,
        date=transaction.date
    )

    # Add the new object to the database session.
    db.add(new_transaction)

    # Save the change to PostgreSQL.
    db.commit()

    # Refresh the object so SQLAlchemy gets values
    # generated by the database, such as the new ID.
    db.refresh(new_transaction)

    return {
        "message": "Transaction created successfully",
        "id": new_transaction.id
    }



@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    # Find the transaction we want to delete.
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    # If the transaction doesn't exist,
    # tell the client it wasn't found.
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    # Mark this object for deletion.
    db.delete(transaction)

    # Permanently save the deletion to PostgreSQL.
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }


@app.put("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):

    # Find the transaction that we want to update.
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    # If it doesn't exist, return a 404.
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    # Validate the transaction type.
    if transaction_data.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be income or expense"
        )

    # Update the existing object's values.
    transaction.amount = transaction_data.amount

    transaction.type = transaction_data.type

    transaction.category = transaction_data.category

    transaction.description = transaction_data.description

    transaction.date = transaction_data.date

    # Save the changes to PostgreSQL.
    db.commit()

    # Refresh the object with the latest database values.
    db.refresh(transaction)

    return transaction