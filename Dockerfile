FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn boto3 openpyxl python-multipart pyxlsb

# Copy application files
COPY app.py .
COPY frontend_html.py .
COPY alfa_pt_lwf.json .
COPY backend/ backend/

# Create data and uploads directories
RUN mkdir -p /app/data /app/uploads

# Expose port
EXPOSE 8000

# Run the app
CMD ["python3", "app.py"]
