# ComfyUI Docker Guide

This guide explains how to run ComfyUI in Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA Docker runtime (for GPU support)
- 16GB+ RAM recommended
- NVIDIA GPU with CUDA 12.6+ support (optional, can run on CPU)

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t comfyui:latest .
```

Or using Docker Compose:

```bash
docker-compose build
```

### 2. Run with Docker Compose

```bash
docker-compose up -d
```

Access ComfyUI at `http://localhost:8188`

### 3. Stop the Container

```bash
docker-compose down
```

## Configuration

### Using Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
CUDA_VISIBLE_DEVICES=0
COMFYUI_PORT=8188
COMFYUI_LISTEN=0.0.0.0
```

### Volume Mounts

The default docker-compose.yml mounts:

- `./models/` - Model storage
- `./input/` - Input images
- `./output/` - Generated outputs
- `./custom_nodes/` - Custom node extensions

### GPU Configuration

For NVIDIA GPUs, the compose file automatically reserves GPU resources. Adjust with:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # Specify GPU device
          capabilities: [gpu]
```

### CPU-Only Mode

Edit docker-compose.yml and remove the GPU section, then start with:

```bash
docker run -it -p 8188:8188 -v $(pwd)/models:/comfyui/models comfyui:latest python main.py --listen 0.0.0.0 --cpu
```

## Running Commands

### Interactive Mode

```bash
docker exec -it comfyui bash
```

### View Logs

```bash
docker-compose logs -f comfyui
```

### Run Custom Command

```bash
docker exec comfyui python main.py --help
```

## Model Management

1. Place model files in `./models/checkpoints/`
2. Place VAE models in `./models/vae/`
3. Place LoRA files in `./models/loras/`
4. Place embeddings in `./models/embeddings/`

Volume mounts ensure persistence between container restarts.

## Performance Tuning

### Memory Limits

Adjust in docker-compose.yml:

```yaml
mem_limit: 32g  # Increase for large models
```

### CPU Threads

```bash
docker run -it -e COMFYUI_CPU_THREADS=8 comfyui:latest
```

## Troubleshooting

### GPU Not Detected

```bash
docker run --gpus all -it comfyui:latest python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory

Increase Docker memory limits or use `--cpu` mode.

### Port Already in Use

Change port mapping in docker-compose.yml:

```yaml
ports:
  - "8189:8188"  # Access at localhost:8189
```

## Advanced Configuration

### Using a Custom Config

```bash
docker run -v $(pwd)/extra_model_paths.yaml:/comfyui/extra_model_paths.yaml comfyui:latest
```

### Custom Node Installation

Place custom nodes in `./custom_nodes/` before building:

```bash
git clone <custom-node-repo> custom_nodes/<name>
docker-compose build
docker-compose up
```

### Multiple Instances

Run multiple containers with different ports:

```bash
docker run -p 8188:8188 --name comfyui1 -d comfyui:latest
docker run -p 8189:8188 --name comfyui2 -d comfyui:latest
```

## Production Deployment

For production use:

1. Use specific version tags: `comfyui:v0.9.2`
2. Add health checks (included in Dockerfile)
3. Use reverse proxy (nginx example in docker-compose.yml)
4. Set resource limits appropriately
5. Use named volumes for persistence
6. Implement backup strategy for models directory
7. Monitor container health with docker stats

## Additional Resources

- [ComfyUI Documentation](https://docs.comfy.org/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Docker Documentation](https://docs.docker.com/)
