from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TransactionCreate, TransactionResponse
from app.models import Transaction, StatusEnum
from app.database import get_db
from app.worker import process_transaction
from sqlalchemy.future import select
from typing import List
import uuid

app = FastAPI()

@app.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(data: TransactionCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    transaction = Transaction(amount=data.amount, currency=data.currency, status=StatusEnum.pending)
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    # Trigger async worker task with Celery
    process_transaction.delay(str(transaction.id))

    return transaction

@app.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).offset(skip).limit(limit))
    transactions = result.scalars().all()
    return transactions

@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    try:
        transaction_uuid = uuid.UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction ID")

    transaction = await db.get(Transaction, transaction_uuid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    # Sample checks for DB connectivity and mock posting service could be added
    # For brevity, return a simple status (expand as needed)
    return {"status": "ok"}
