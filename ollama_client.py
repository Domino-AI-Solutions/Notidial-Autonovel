#!/usr/bin/env python3
"""
Centralized client for interacting with the Ollama API.
Handles model calls, error handling, and verbose logging.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
REQUEST_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", 180)) # 3 minute timeout

# Check for verbose logging flag from the environment (set by launcher.py)
IS_VERBOSE = os.getenv("AUTOWRITE_VERBOSE_LOGGING") == "1"

def call_model(model: str, prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """
    Calls an Ollama model and returns the response.
    Includes error handling and optional verbose logging.
    """
    if IS_VERBOSE:
        print("\n" + "="*20 + f" VERBOSE: Calling Model: {model} " + "="*20)
        print(f"PROMPT:\n---\n{prompt}\n---\n")

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()["message"]["content"]
            if IS_VERBOSE:
                print(f"RESPONSE:\n---\n{result}\n---\n" + "="*60 + "\n")
            return result
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"[ERROR] Model call failed: {e}")
        if IS_VERBOSE:
            print("="*60 + "\n")
        return ""