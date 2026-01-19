# Multi-stage build for ComfyUI
FROM nvidia/cuda:12.6.3-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    ca-certificates \
    python3.13 \
    python3.13-dev \
    python3.13-distutils \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.13 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

WORKDIR /comfyui

# Copy requirements files
COPY requirements.txt manager_requirements.txt ./

# Install Python dependencies
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
RUN pip install -r requirements.txt

# Install manager dependencies (optional, uncomment if needed)
# RUN pip install -r manager_requirements.txt

# Copy application code
COPY . .

# Create directories for models and outputs
RUN mkdir -p models/checkpoints models/vae models/loras models/embeddings input output

# Expose port
EXPOSE 8188

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8188/ || exit 1

# Default command
CMD ["python", "main.py", "--listen", "0.0.0.0"]
