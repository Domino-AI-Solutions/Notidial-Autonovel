"""
Central configuration for the Automatic-Writing pipeline.
Defines all model names, paths, and shared settings.
"""
from pathlib import Path

# --- Core Paths ---
BASE_DIR = Path(__file__).resolve().parent
LAYERS_DIR = BASE_DIR / "layers"
CHAPTERS_DIR = LAYERS_DIR / "chapters"
ART_DIR = BASE_DIR / "art"
AUDIO_OUTPUT_DIR = BASE_DIR / "audiobook"

# --- Model Configuration ---
REASONING_MODEL = "qwen2:7b"
WRITING_MODEL = "llama3.1:8b"
JUDGE_MODEL = "qwen2:7b-instruct"

# --- Ensure Directories Exist ---
LAYERS_DIR.mkdir(exist_ok=True)
CHAPTERS_DIR.mkdir(exist_ok=True)
ART_DIR.mkdir(exist_ok=True)
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)

# --- Ollama Client Configuration ---
OLLAMA_HOST = "http://localhost:11434"
REQUEST_TIMEOUT = 180  # 3 minutes

# --- TTS Configuration ---
REFERENCE_VOICE_PATH = ART_DIR / "reference_voice.wav"
