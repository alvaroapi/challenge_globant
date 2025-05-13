# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

ENTRYPOINT ["./entrypoint.sh"]

# Expose port 8000
EXPOSE 8000


# Run migrations and start server
# Note: Running migrations at container start might not be ideal for production.
# Consider a separate migration step or entrypoint script.
# CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate"]

