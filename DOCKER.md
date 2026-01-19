# ComfyUI Docker Guide

This guide explains how to run ComfyUI in Docker with two variants:

1. **Full Version** (with GPU) - For executing workflows
2. **Web UI Only** (CPU) - For building/designing workflows

## Prerequisites

### Full Version
- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA Docker runtime (for GPU support)
- 16GB+ RAM recommended
- NVIDIA GPU with CUDA 12.6+ support

### Web UI Only
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ RAM (minimal)
- No GPU required

## Quick Start

### Option A: Full Version (GPU - Workflow Execution)

#### 1. Build the Docker Image

```bash
docker build -t comfyui:latest .
```

Or using Docker Compose:

```bash
docker-compose build
```

#### 2. Run with Docker Compose

```bash
docker-compose up -d
```

Access ComfyUI at `http://localhost:8188`

#### 3. Stop the Container

```bash
docker-compose down
```

---

### Option B: Web UI Only (CPU - Workflow Builder)

Lightweight version for designing workflows on a PC without GPU. Workflows can later be executed on another machine with the full version.

#### 1. Build the Image

```bash
docker build -f Dockerfile.webui -t comfyui-webui:latest .
```

Or using Docker Compose:

```bash
docker-compose -f docker-compose.webui.yml build
```

#### 2. Run the Web UI

```bash
docker-compose -f docker-compose.webui.yml up -d
```

Access the workflow designer at `http://localhost:8188`

#### 3. Stop the Container

```bash
docker-compose -f docker-compose.webui.yml down
```

**Benefits:**
- ~500MB image (vs 5GB+)
- Minimal RAM usage (2GB vs 16GB+)
- No GPU required
- Fast startup
- Perfect for workflow design and sharing
- Export workflows as JSON to run on full version

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

## Switching Between Versions

### Run Full Version Then Switch to Web UI

```bash
# Stop full version
docker-compose down

# Start web UI only
docker-compose -f docker-compose.webui.yml up -d
```

### Run Both Versions Simultaneously

Use different ports:

```bash
# Full version on port 8188
docker-compose up -d

# Web UI on port 8189
docker-compose -f docker-compose.webui.yml up -d -p 8189:8188
```

## Troubleshooting

### Web UI Version Not Showing Nodes

The web UI version won't execute workflows. To test execution:
1. Export workflow as JSON from web UI
2. Import on full version or use ComfyUI API
3. No execution happens in web UI-only mode

### GPU Not Detected (Full Version)

```bash
docker run --gpus all -it comfyui:latest python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory

- Full version: Increase Docker memory limits or use `--cpu` mode
- Web UI: Should use <500MB normally

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

## Workflow Export/Import

### Export from Web UI Version
1. Design workflow in web UI
2. Use `Ctrl+S` to save workflow as JSON
3. Download the JSON file

### Import on Full Version
1. Place JSON in a shared volume
2. Load in full ComfyUI instance
3. Execute with your GPU

### Using ComfyUI API
Export the workflow and use the REST API:

```bash
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

## Production Deployment

For production use:

1. Use specific version tags: `comfyui:v0.9.2`
2. Add health checks (included in both Dockerfiles)
3. Use reverse proxy (nginx example in docker-compose.yml)
4. Set resource limits appropriately
5. Use named volumes for persistence
6. Implement backup strategy for models directory
7. Monitor container health with docker stats

### Multi-Environment Setup
- **Dev Machine**: Web UI version for workflow design
- **Production Machine**: Full version for execution
- **Shared Storage**: NFS or S3 for workflow files

## Additional Resources

- [ComfyUI Documentation](https://docs.comfy.org/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Docker Documentation](https://docs.docker.com/)
