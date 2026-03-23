from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Iterable

import srt


def segments_to_plain_text(segments: Iterable[dict]) -> str:
    """Flatten subtitle segments into a readable paragraph block for the UI."""
    return "\n".join(segment["text"] for segment in segments)


def _to_srt_subtitles(segments: Iterable[dict]) -> list[srt.Subtitle]:
    """Convert normalized segments into srt.Subtitle objects."""
    subtitles = []
    for index, segment in enumerate(segments, start=1):
        subtitles.append(
            srt.Subtitle(
                index=index,
                start=timedelta(seconds=float(segment["start"])),
                end=timedelta(seconds=float(segment["end"])),
                content=segment["text"].strip(),
            )
        )
    return subtitles


def _format_vtt_timestamp(seconds: float) -> str:
    """Format timestamps for WebVTT using milliseconds."""
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"


def write_srt_file(segments: Iterable[dict], destination: str | Path) -> Path:
    """Write subtitle segments to an .srt file."""
    output_path = Path(destination).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subtitle_text = srt.compose(_to_srt_subtitles(segments))
    # utf-8-sig improves compatibility with Windows editors and some subtitle tools.
    output_path.write_text(subtitle_text, encoding="utf-8-sig")
    return output_path


def write_vtt_file(segments: Iterable[dict], destination: str | Path) -> Path:
    """Write subtitle segments to a .vtt file."""
    output_path = Path(destination).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["WEBVTT", ""]
    for segment in segments:
        lines.append(f"{_format_vtt_timestamp(segment['start'])} --> {_format_vtt_timestamp(segment['end'])}")
        lines.append(segment["text"].strip())
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8-sig")
    return output_path


def write_subtitle_files(
    segments: Iterable[dict],
    srt_destination: str | Path,
    vtt_destination: str | Path,
) -> tuple[Path, Path]:
    """Generate both SRT and VTT outputs from the same subtitle segment list."""
    srt_path = write_srt_file(segments, srt_destination)
    vtt_path = write_vtt_file(segments, vtt_destination)
    return srt_path, vtt_path
