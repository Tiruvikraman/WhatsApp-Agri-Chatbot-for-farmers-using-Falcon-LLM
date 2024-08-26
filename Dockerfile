# Use Python 3.9 slim image as the base
FROM python:3.9-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    unzip \
    curl \
    ca-certificates \
    gnupg \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator1 \
    libgbm-dev \
    libgtk-3-0 \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /code

# Create necessary directories
RUN mkdir -p /code/uploads /code/chroma_db

# Add and use a non-root user
RUN useradd -ms /bin/sh myuser

# Set ownership and permissions
RUN chown -R myuser:myuser /code && \
    chmod -R 755 /code/chroma_db && \
    chmod -R 775 /code/uploads

RUN apt-get update && apt-get install -y  tesseract-ocr

# Switch to non-root user
USER myuser

# Copy and install Python dependencies
COPY --chown=myuser:myuser ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code
COPY --chown=myuser:myuser . /code

# Default command to run the application
CMD ["python", "app.py"]