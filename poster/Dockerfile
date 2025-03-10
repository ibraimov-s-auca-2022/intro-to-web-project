# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

COPY /poster/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY /poster .

# Run the application
CMD ["python", "main.py"]

