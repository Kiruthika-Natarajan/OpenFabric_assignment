# High Performance Transaction Processing Service

## Overview

This service acts as an intermediary for financial transactions, providing fast API responses (<100ms), ensuring no data loss or duplicate transactions, and reliable posting to a mock posting service.

## Architecture

- FastAPI for the HTTP API.
- PostgreSQL for persistent storage of transactions.
- Celery + Redis for async processing and retries.
- Docker Compose setup including provided vinhopenfabric/mock-posting-service image.

## Async Worker Design

- Transactions created with status `pending`.
- Celery worker picks transactions, marks them `processing`, then posts them to the mock service.
- On successful post, status set to `completed`.
- Failures trigger retries with exponential backoff (max 5 attempts).
- Duplicate posts prevented by checking transaction status and unique UUID.

## Load Testing

- `k6` script included to simulate concurrent POST requests.
- Run `k6 run loadtest.js` to verify system throughput and latency.

## Running the Service

