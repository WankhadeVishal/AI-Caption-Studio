from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def check_ffmpeg() -> bool:
    """Return True when the ffmpeg executable is available on PATH."""
    return shutil.which("ffmpeg") is not None


def _escape_subtitle_path_for_ffmpeg(subtitle_path: Path) -> str:
    """Escape a subtitle path for the FFmpeg subtitles filter, including Windows drive letters."""
    escaped = subtitle_path.resolve().as_posix()
    if len(escaped) > 1 and escaped[1] == ":":
        escaped = escaped[0] + "\\:" + escaped[2:]
    escaped = escaped.replace("'", r"\'")
    escaped = escaped.replace("[", r"\[").replace("]", r"\]")
    return escaped


def burn_subtitles_into_video(
    video_path: str | Path,
    subtitle_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Burn SRT subtitles into a video using FFmpeg."""
    source_video = Path(video_path).resolve()
    source_subtitle = Path(subtitle_path).resolve()
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not source_video.exists():
        raise FileNotFoundError(f"Video file not found: {source_video}")
    if not source_subtitle.exists():
        raise FileNotFoundError(f"Subtitle file not found: {source_subtitle}")
    if not check_ffmpeg():
        raise EnvironmentError("FFmpeg is not installed or not available on PATH.")

    subtitle_filter_parts = [
        f"subtitles='{_escape_subtitle_path_for_ffmpeg(source_subtitle)}'",
        "charenc=UTF-8",
        "force_style='Fontname=Segoe UI,Fontsize=18,OutlineColour=&H40000000,BorderStyle=3'",
    ]
    subtitle_filter = ":".join(subtitle_filter_parts)

    # We re-encode the video stream so the subtitles become part of the exported MP4.
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_video),
        "-vf",
        subtitle_filter,
        "-c:a",
        "copy",
        str(destination),
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "FFmpeg failed while burning subtitles into the video.")

    return destination
