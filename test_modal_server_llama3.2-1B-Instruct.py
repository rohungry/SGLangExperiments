import modal

# ---------------------------------------------------------------------------
# Model config
# ---------------------------------------------------------------------------
MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"
#"meta-llama/Llama-3.2-1B"
# Commit hash on HF for Llama-3.2-1B from 2024-10-24 (pins weights & config).
MODEL_REVISION = '9213176726f574b556790deb65791e0c5aa438b6'
# For regular llama-3.2-1B"4e20de362430cd3b72f300e6b0f18e50e7166e08"

# NOTE on the image: you asked for `lmsysorg/sglang:main-cann8.5.0-910b`, but
# that tag is built for Huawei Ascend 910B NPUs (CANN = Huawei's stack) and
# has no CUDA runtime — it cannot execute on an NVIDIA A10. The correct
# "latest" tag for NVIDIA GPUs is `lmsysorg/sglang:latest`. To pin a version,
# swap in something like `lmsysorg/sglang:v0.4.8.post1-cu126`.
SGLANG_IMAGE = "lmsysorg/sglang:latest"

PORT = 30000
MINUTES = 60

# ---------------------------------------------------------------------------
# Container image
# ---------------------------------------------------------------------------
# `.entrypoint([])` clears the image's default ENTRYPOINT so Modal can exec
# its own process. `hf_transfer` speeds up the model download.
image = (
    modal.Image.from_registry(SGLANG_IMAGE)
    .entrypoint([])
    .pip_install("hf_transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

app = modal.App("llama-sglang-test", image=image)

# Cache HF downloads across container restarts so we don't re-pull 1B weights.
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)

N_GPUS = 1
# GPU = f"A10:{N_GPUS}"
TARGET_INPUTS = 10
# ---------------------------------------------------------------------------
# Web server
# ---------------------------------------------------------------------------
@app.function(
    gpu="A10",
    secrets=[modal.Secret.from_name('HF_TOKEN')],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=30 * MINUTES,
    scaledown_window=15 * MINUTES,
)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=PORT, startup_timeout=10 * MINUTES)
def serve():
    import subprocess

    cmd = [
        "python3", "-m", "sglang.launch_server",
        "--model-path", MODEL_NAME,
        "--revision", MODEL_REVISION,   # pins to your 2024-10-24 commit
        "--host", "0.0.0.0",
        "--port", str(PORT),
        # Llama-3.2-1B is tiny; cap memory so SGLang doesn't grab everything.
        "--tp", f"{N_GPUS}", # use all GPUs to split up tensor-parallel operations
        "--cuda-graph-max-bs", f"{TARGET_INPUTS * 2}", # only capture CUDA graphs for batch sizes we're likely to observe
        "--enable-metrics",  # expose metrics endpoints for telemetry
        "--decode-log-interval",  "100", # how often to log during decoding, in tokens
        "--mem-fraction-static", "0.80",
    ]
    # Popen (not run) — web_server expects the process to stay alive in bg.
    subprocess.Popen(" ".join(cmd), shell=True)

### Use for debugging purposes - e.g if your HF_TOKEN isn't setup as a modal secret
# @app.function(secrets=[modal.Secret.from_name("huggingface-secret")])
# def whoami():
#     import os
#     from huggingface_hub import HfApi
#     tok = os.environ.get("HF_TOKEN")
#     print("HF_TOKEN present:", bool(tok), "| starts with:", (tok or "")[:7])
#     print("whoami:", HfApi().whoami(token=tok))
#     # Try to fetch the gated file specifically
#     from huggingface_hub import hf_hub_download
#     path = hf_hub_download(
#         "meta-llama/Llama-3.2-1B", "config.json",
#         revision="4e20de362430cd3b72f300e6b0f18e50e7166e08", token=tok,
#     )
#     print("config.json ->", path)