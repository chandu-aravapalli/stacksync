FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential clang pkg-config zlib1g-dev libprotobuf-dev \
    protobuf-compiler libnl-route-3-dev libcap-dev \
    libseccomp-dev libssl-dev libzstd-dev \
    flex bison ca-certificates curl git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Build nsjail from source
RUN git clone https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && \
    make && \
    mv nsjail /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/nsjail

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . /app
WORKDIR /app

# Create a non-root user
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8080
CMD ["python", "app.py"]
