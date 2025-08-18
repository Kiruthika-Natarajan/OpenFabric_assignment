import os
from celery import Celery
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Transaction, StatusEnum
from app.utils import post_transaction_to_mock_service
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
POSTING_SERVICE_URL = os.getenv("POSTING_SERVICE_URL")

celery_app = Celery('worker', broker=REDIS_URL, backend=REDIS_URL)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@celery_app.task(bind=True, max_retries=5)
def process_transaction(self, transaction_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_process_task(self, transaction_id, self.request.retries))

async def _process_task(self, transaction_id, retry_count):
    async with async_session() as session:
        transaction = await session.get(Transaction, transaction_id)
        if not transaction or transaction.status != StatusEnum.pending:
            return

        transaction.status = StatusEnum.processing
        await session.commit()

        try:
            # Attempt posting
            await post_transaction_to_mock_service(transaction)
            transaction.status = StatusEnum.completed
            transaction.error = None
        except Exception as e:
            if retry_count < self.max_retries:
                raise self.retry(exc=e, countdown=2 ** retry_count)
            transaction.status = StatusEnum.failed
            transaction.error = str(e)

        await session.commit()
