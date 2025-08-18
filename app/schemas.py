from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import Optional

class StatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class TransactionCreate(BaseModel):
    amount: float
    currency: str

class TransactionResponse(BaseModel):
    id: UUID
    amount: float
    currency: str
    status: StatusEnum
    error: Optional[str] = None

    class Config:
        orm_mode = True
