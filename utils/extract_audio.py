from __future__ import annotations

from pathlib import Path

try:
    # MoviePy 2.x exposes VideoFileClip at the package root.
    from moviepy import VideoFileClip
except ImportError:
    try:
        # MoviePy 1.x keeps VideoFileClip under moviepy.editor.
        from moviepy.editor import VideoFileClip
    except ImportError as exc:
        raise ImportError(
            "MoviePy is not installed correctly. Run 'python -m pip install moviepy' "
            "or reinstall dependencies with 'python -m pip install -r requirements.txt'."
        ) from exc


def extract_audio_from_video(video_path: str | Path, audio_path: str | Path) -> Path:
    """Extract mono 16kHz WAV audio from a video file for Whisper transcription."""
    source = Path(video_path).resolve()
    destination = Path(audio_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        raise FileNotFoundError(f"Video file not found: {source}")

    video_clip = None
    audio_clip = None

    try:
        video_clip = VideoFileClip(str(source))
        audio_clip = video_clip.audio

        if audio_clip is None:
            raise ValueError("The uploaded video does not contain an audio track.")

        # Whisper works well with 16kHz mono WAV input, so we normalize the export here.
        audio_clip.write_audiofile(
            str(destination),
            fps=16000,
            codec="pcm_s16le",
            ffmpeg_params=["-ac", "1"],
            logger=None,
        )
    finally:
        if audio_clip is not None:
            audio_clip.close()
        if video_clip is not None:
            video_clip.close()

    return destination
