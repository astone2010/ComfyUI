#!/usr/bin/env python
"""Validate a MiniMax H3 Plan JSON offline, without queueing a render.

Run with ComfyUI's own interpreter:
    C:/APPS/ComfyUI/.venv/Scripts/python.exe validate_plan.py \
        --plan plan.json --run probe --width 768 --height 960

Prints the normalized summary/plan_hash and per-shot fields on success; exits 2 on failure.
Builds through the pack's own MiniMaxH3ChainPlan().build(), which is the same normalization a
queue applies, so a pass here means the plan schema/timing will not bounce at preflight.
"""
import argparse
import importlib.util
import json
import os
import sys

PACK = r"C:/APPS/ComfyUI/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop"


def load_chain_nodes(pack=PACK):
    """chain_nodes.py uses relative imports, so load it package-style."""
    if r"C:/APPS/ComfyUI" not in sys.path:
        sys.path.insert(0, r"C:/APPS/ComfyUI")
    spec = importlib.util.spec_from_file_location(
        "h3pack", os.path.join(pack, "chain_nodes.py"), submodule_search_locations=[pack])
    module = importlib.util.module_from_spec(spec)
    sys.modules["h3pack"] = module
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, help="path to the plan JSON (authoring shape)")
    p.add_argument("--run", default="plan_probe", help="throwaway run name")
    p.add_argument("--width", type=int, default=768)
    p.add_argument("--height", type=int, default=960)
    p.add_argument("--context-length", type=int, default=22)
    p.add_argument("--audio-context-length", type=int, default=22)
    p.add_argument("--steps", type=int, default=8)
    p.add_argument("--seconds", type=float, default=15.0)
    p.add_argument("--steps-default", dest="default_steps", type=int, default=None,
                   help="defaults.steps fallback (defaults to --steps)")
    p.add_argument("--continuation-mode", default="guide")
    p.add_argument("--anchor-mode", default="head")
    p.add_argument("--crop", default="center")
    p.add_argument("--encode-mode", default="video")
    p.add_argument("--audio-mode", default="generated_audio")
    p.add_argument("--crf", type=int, default=20)
    p.add_argument("--blend", type=int, default=5)
    args = p.parse_args()

    for axis in (args.width, args.height):
        if axis < 32 or axis > 4096 or axis % 32:
            print(f"FAIL: {axis} is not a multiple of 32 between 32 and 4096")
            return 2

    plan_json = open(args.plan, encoding="utf-8").read()
    try:
        json.loads(plan_json)
    except ValueError as exc:
        print(f"FAIL: plan is not valid JSON: {exc}")
        return 2

    cn = load_chain_nodes()
    try:
        built = cn.MiniMaxH3ChainPlan().build(
            plan_json=plan_json, run_name=args.run, generation_fingerprint="",
            width=args.width, height=args.height, context_length=args.context_length,
            encode_mode=args.encode_mode, anchor_mode=args.anchor_mode, crop=args.crop,
            audio_mode=args.audio_mode, audio_context_length=args.audio_context_length,
            default_duration_seconds=args.seconds,
            default_steps=args.default_steps or args.steps, base_seed=0,
            segment_crf=args.crf, video_blend_frames=args.blend,
            continuation_mode=args.continuation_mode, chain_policy=None, project_assets=None)[0]
    except Exception as exc:  # noqa: BLE001 - report the pack's own message verbatim
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return 2

    print("BUILD OK")
    print("summary:", built.get("summary"))
    print("plan_hash:", built.get("plan_hash"))
    print("compatibility:", json.dumps(built.get("compatibility"), sort_keys=True))
    for shot in built.get("shots", []):
        prompt = shot.get("scene_prompt", shot.get("prompt"))
        size = len(json.dumps(prompt)) if prompt is not None else 0
        print(f"  scene {shot.get('index')}: {shot.get('id')} seed={shot.get('seed')} "
              f"steps={shot.get('steps')} raw_frames={shot.get('raw_frames')} prompt_chars={size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
