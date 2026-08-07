"""
AWS Lambda handler using Mangum adapter.
Wraps the FastAPI app for API Gateway + Lambda deployment.
"""

from mangum import Mangum
from api.main import app

# Mangum converts API Gateway events to ASGI requests for FastAPI
handler = Mangum(app, lifespan="off")
