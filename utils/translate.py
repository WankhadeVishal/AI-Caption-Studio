from __future__ import annotations

import os
from typing import Iterable

from openai import OpenAI


def _chunk_segments(segments: list[dict], size: int = 40) -> list[list[dict]]:
    """Chunk subtitle segments to keep translation requests compact and aligned."""
    return [segments[index : index + size] for index in range(0, len(segments), size)]


def _build_payload(chunk: list[dict]) -> str:
    """Serialize segment text in a stable numbered format for translation."""
    return "\n".join(f"{index + 1}|||{segment['text']}" for index, segment in enumerate(chunk))


def _parse_translation(response_text: str, expected_count: int) -> list[str]:
    """Parse the model output and recover translated lines in their original order."""
    translated_by_index: dict[int, str] = {}

    for line in response_text.splitlines():
        if "|||" not in line:
            continue
        prefix, translated_text = line.split("|||", 1)
        prefix = prefix.strip()
        if prefix.isdigit():
            translated_by_index[int(prefix)] = translated_text.strip()

    if len(translated_by_index) != expected_count:
        raise ValueError("The translation response did not preserve subtitle line numbering.")

    return [translated_by_index[index] for index in range(1, expected_count + 1)]


def translate_segments(segments: Iterable[dict], target_language: str, model_name: str = "gpt-4o-mini") -> list[dict]:
    """Translate subtitle text with the OpenAI API while preserving timestamps."""
    source_segments = [dict(segment) for segment in segments]

    if not source_segments:
        return source_segments

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set. Translation cannot run without an API key.")

    client = OpenAI(api_key=api_key)
    translated_segments: list[dict] = []

    for chunk in _chunk_segments(source_segments):
        payload = _build_payload(chunk)
        response = client.chat.completions.create(
            model=model_name,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You translate subtitle lines. Preserve the line numbering exactly in the format "
                        "N|||translated text. Return one translated line for every input line and nothing else."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Translate the subtitle text into {target_language}. Keep meaning natural and concise.\n\n"
                        f"{payload}"
                    ),
                },
            ],
        )
        translated_lines = _parse_translation(response.choices[0].message.content or "", len(chunk))

        for segment, translated_text in zip(chunk, translated_lines):
            translated_segment = dict(segment)
            translated_segment["text"] = translated_text
            translated_segments.append(translated_segment)

    return translated_segments
