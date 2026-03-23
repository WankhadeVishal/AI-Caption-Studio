from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import whisper


@lru_cache(maxsize=2)
def load_whisper_model(model_name: str = "base"):
    """Load and cache the Whisper model so repeated app runs stay responsive."""
    return whisper.load_model(model_name)


def transcribe_audio(audio_path: str | Path, model_name: str = "base", language: str | None = None) -> dict:
    """Transcribe an audio file and normalize Whisper segments into a simple structure."""
    source = Path(audio_path).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Audio file not found: {source}")

    model = load_whisper_model(model_name)

    # fp16 is disabled for broader Windows CPU compatibility.
    transcription_options = {
        "fp16": False,
        "verbose": False,
        "task": "transcribe",
    }
    if language:
        # Language hints improve subtitle accuracy when the spoken language is known.
        transcription_options["language"] = language

    raw_result = model.transcribe(str(source), **transcription_options)

    segments = []
    for segment in raw_result.get("segments", []):
        text = segment.get("text", "").strip()
        if not text:
            continue
        segments.append(
            {
                "start": float(segment["start"]),
                "end": float(segment["end"]),
                "text": text,
            }
        )

    if not segments:
        raise ValueError("Whisper completed, but no speech segments were detected in the audio.")

    return {
        "text": raw_result.get("text", "").strip(),
        "language": raw_result.get("language", "unknown"),
        "segments": segments,
    }
