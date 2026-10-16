FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    ffmpeg \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

WORKDIR /comfyui

COPY requirements.txt ./

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130 && \
    grep -v '^sageattention' requirements.txt > /tmp/requirements.txt && \
    pip install -r /tmp/requirements.txt

COPY . .

RUN mkdir -p custom_nodes input models output temp user

EXPOSE 8188

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl --fail --silent http://localhost:8188/ > /dev/null || exit 1

CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
