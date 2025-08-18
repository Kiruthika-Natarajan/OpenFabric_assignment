import httpx
import os

POSTING_SERVICE_URL = os.getenv("POSTING_SERVICE_URL")

async def post_transaction_to_mock_service(transaction):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{POSTING_SERVICE_URL}/transactions", json={
            "transactionId": str(transaction.id),
            "amount": transaction.amount,
            "currency": transaction.currency,
        })
        response.raise_for_status()
        return response
