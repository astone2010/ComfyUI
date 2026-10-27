@echo off
REM Launch ComfyUI from the pinned .venv WITHOUT letting uv re-sync the environment.
REM Plain "uv run python main.py" prunes every package not listed in pyproject.toml/uv.lock
REM (cv2, numba, piexif, dynamicprompts, scikit-image, soundfile, matplotlib, ComfyUI-Manager's
REM deps ...) which silently breaks custom nodes. --no-sync keeps the venv as installed.
cd /d "%~dp0"
uv run --no-sync python main.py %*
