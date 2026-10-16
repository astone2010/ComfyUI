# ComfyUI Docker setup

This setup runs the full NVIDIA GPU version of ComfyUI and keeps runtime data on the host.

## Start

Docker Desktop must use the WSL 2 engine and have access to the drive containing the additional models. The configured default is `F:/Comfyui/models`.

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose logs -f comfyui
```

Open <http://localhost:8188>. Stop it with:

```powershell
docker compose down
```

## Storage

The Compose service mounts these host directories:

- `./models` as ComfyUI's writable, primary model directory.
- `F:/Comfyui/models` as the read-only additional model directory.
- `./custom_nodes`, `./input`, `./output`, `./temp`, and `./user` as writable runtime directories.

Change `COMFYUI_ADDITIONAL_MODELS` in `.env` if the shared model directory moves. Keep forward slashes for a Windows path. The category mapping is in `extra_model_paths.docker.yaml`; it includes both standard ComfyUI folders and the additional folders currently present in the shared tree.

The native Windows `extra_model_paths.yaml` is intentionally not copied into the image. It contains a Windows path that is not valid inside a Linux container.

## Useful checks

```powershell
docker compose config
docker compose exec comfyui python -c "import torch; print(torch.cuda.get_device_name(0))"
docker compose exec comfyui ls /models/additional/checkpoints
docker compose ps
```

Custom node source is mounted into the container. Python packages required by individual custom nodes must also be installed in the image; rebuild after adding them to the Dockerfile or manage them from inside the container.
