"""Main entry point for the application."""

import uvicorn

from src.endpoints import app


def run_sds_API():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
