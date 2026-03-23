from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st

from utils.burn_subtitles import burn_subtitles_into_video, check_ffmpeg
from utils.extract_audio import extract_audio_from_video
from utils.generate_subtitles import segments_to_plain_text, write_subtitle_files
from utils.transcribe import transcribe_audio
from utils.translate import translate_segments


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create required directories once at startup so the app is ready on first run.
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


LANGUAGE_OPTIONS = [
    "Original language (no translation)",
    "English",
    "Spanish",
    "French",
    "German",
    "Japanese",
]

SPEECH_LANGUAGE_OPTIONS = [
    "Auto detect",
    "English",
    "Spanish",
    "French",
    "German",
    "Japanese",
]

LANGUAGE_CODE_MAP = {
    "Auto detect": None,
    "Original language (no translation)": None,
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
}

LANGUAGE_NAME_MAP = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
}


def inject_styles() -> None:
    """Apply a custom dark glassmorphism theme to the Streamlit app."""
    st.markdown(
        """
        <style>
            :root {
                --bg-start: #050816;
                --bg-end: #0c1831;
                --panel: rgba(11, 20, 37, 0.68);
                --panel-strong: rgba(16, 28, 49, 0.88);
                --border: rgba(140, 181, 255, 0.18);
                --accent: #5de4c7;
                --accent-2: #72a8ff;
                --text: #eef4ff;
                --muted: #9fb2d4;
                --warning: #ffcf75;
                --success: #6bf7b1;
                --shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(93, 228, 199, 0.14), transparent 35%),
                    radial-gradient(circle at top right, rgba(114, 168, 255, 0.16), transparent 28%),
                    linear-gradient(135deg, var(--bg-start), var(--bg-end));
                color: var(--text);
                font-family: "Bahnschrift", "Segoe UI", sans-serif;
            }

            .block-container {
                padding-top: 3rem;
                padding-bottom: 2rem;
                max-width: 1180px;
            }

            h1, h2, h3 {
                color: var(--text);
                font-family: "Georgia", "Palatino Linotype", serif;
                letter-spacing: 0.03em;
            }

            .hero-card,
            .glass-card,
            div[data-testid="stFileUploader"],
            div[data-testid="stMetric"],
            div[data-testid="stDataFrame"],
            div[data-testid="stAlert"] {
                background: var(--panel);
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                border: 1px solid var(--border);
                border-radius: 22px;
                box-shadow: var(--shadow);
            }

            .hero-card {
                padding: 1.8rem;
                margin-bottom: 1.2rem;
                position: relative;
                overflow: hidden;
            }

            .hero-card::after {
                content: "";
                position: absolute;
                inset: auto -120px -120px auto;
                width: 240px;
                height: 240px;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(93, 228, 199, 0.26), transparent 65%);
                pointer-events: none;
            }

            .glass-card {
                padding: 1.1rem 1.2rem;
                margin-bottom: 1rem;
            }

            .eyebrow {
                color: var(--accent);
                text-transform: uppercase;
                letter-spacing: 0.18em;
                font-size: 0.82rem;
                margin-bottom: 0.45rem;
                font-weight: 700;
            }

            .hero-title {
                font-size: clamp(2.2rem, 5vw, 4rem);
                line-height: 1.02;
                margin: 0 0 0.65rem 0;
            }

            .hero-subtitle {
                color: var(--muted);
                font-size: 1.02rem;
                max-width: 760px;
                margin: 0;
            }

            .chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-top: 1rem;
            }

            .chip {
                padding: 0.55rem 0.9rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: var(--text);
                font-size: 0.9rem;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.8rem 1rem;
                border-radius: 16px;
                background: rgba(107, 247, 177, 0.12);
                border: 1px solid rgba(107, 247, 177, 0.24);
                color: var(--success);
                font-weight: 700;
                animation: pulseGlow 1.8s ease-in-out infinite;
            }

            @keyframes pulseGlow {
                0% { box-shadow: 0 0 0 0 rgba(107, 247, 177, 0.20); }
                70% { box-shadow: 0 0 0 16px rgba(107, 247, 177, 0); }
                100% { box-shadow: 0 0 0 0 rgba(107, 247, 177, 0); }
            }

            .metric-label {
                color: var(--muted);
                margin-bottom: 0.35rem;
                font-size: 0.88rem;
            }

            .metric-value {
                font-size: 1.1rem;
                font-weight: 700;
            }

            .hint {
                color: var(--muted);
                font-size: 0.92rem;
            }

            .stButton > button,
            .stDownloadButton > button {
                width: 100%;
                border-radius: 16px;
                border: 1px solid rgba(93, 228, 199, 0.25);
                background: linear-gradient(135deg, rgba(93, 228, 199, 0.18), rgba(114, 168, 255, 0.20));
                color: var(--text);
                font-weight: 700;
                min-height: 3rem;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: rgba(93, 228, 199, 0.45);
                transform: translateY(-1px);
            }

            .stProgress > div > div {
                background: linear-gradient(90deg, var(--accent), var(--accent-2));
            }

            .stSelectbox label,
            .stCheckbox label,
            .stFileUploader label {
                color: var(--text) !important;
                font-weight: 600;
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-top: 1.5rem;
                }

                .hero-card {
                    padding: 1.2rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def save_uploaded_video(uploaded_file: Any) -> Path:
    """Persist the uploaded MP4 to disk with a unique name."""
    extension = Path(uploaded_file.name).suffix.lower() or ".mp4"
    safe_stem = Path(uploaded_file.name).stem.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{safe_stem}_{timestamp}_{uuid4().hex[:8]}{extension}"
    destination = UPLOAD_DIR / file_name
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def build_output_paths(video_path: Path) -> dict[str, Path]:
    """Prepare consistent output file paths based on the uploaded video name."""
    stem = video_path.stem
    output_folder = OUTPUT_DIR / stem
    output_folder.mkdir(parents=True, exist_ok=True)
    return {
        "folder": output_folder,
        "audio": output_folder / f"{stem}.wav",
        "srt": output_folder / f"{stem}.srt",
        "vtt": output_folder / f"{stem}.vtt",
        "captioned_video": output_folder / f"{stem}_captioned.mp4",
    }


def format_timestamp(seconds: float) -> str:
    """Render a float-second timestamp into HH:MM:SS.mmm format."""
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"


def render_hero() -> None:
    """Top-of-page hero section with a product-style introduction."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">AI Video Caption Studio</div>
            <h1 class="hero-title">Upload a video, generate subtitles, and export a captioned cut.</h1>
            <p class="hero-subtitle">
                This app extracts audio, transcribes speech with Whisper, optionally translates subtitle text,
                exports both SRT and VTT, and burns captions into the final MP4 using FFmpeg.
            </p>
            <div class="chip-row">
                <div class="chip">Whisper base</div>
                <div class="chip">Streamlit UI</div>
                <div class="chip">SRT + VTT</div>
                <div class="chip">FFmpeg burn-in</div>
                <div class="chip">Windows friendly</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def needs_openai_transform(speech_language: str, target_language: str) -> bool:
    """Return True when the selected subtitle mode requires the OpenAI API."""
    if target_language == "Original language (no translation)":
        return False
    if speech_language == "Auto detect":
        return True
    return target_language != speech_language


def render_summary(result: dict[str, Any]) -> None:
    """Render metrics that summarize the finished processing run."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">Detected language</div>
                <div class="metric-value">{result.get('detected_language', 'Unknown').title()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">Subtitle segments</div>
                <div class="metric-value">{len(result['segments'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">Subtitle language</div>
                <div class="metric-value">{result['output_subtitle_language']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def run_pipeline(
    video_path: Path,
    speech_language: str,
    target_language: str,
    should_burn_subtitles: bool,
    progress_bar: Any,
    status_placeholder: Any,
) -> dict[str, Any]:
    """Execute the full caption-generation pipeline for a single uploaded video."""
    output_paths = build_output_paths(video_path)
    speech_language_code = LANGUAGE_CODE_MAP.get(speech_language)
    warnings: list[str] = []

    status_placeholder.info("Extracting audio from the uploaded video...")
    progress_bar.progress(10)
    audio_path = extract_audio_from_video(video_path, output_paths["audio"])

    status_placeholder.info("Transcribing speech with Whisper...")
    progress_bar.progress(35)
    transcript = transcribe_audio(audio_path, model_name="base", language=speech_language_code)
    segments = transcript["segments"]
    detected_language_code = transcript.get("language", "unknown")
    detected_language_name = LANGUAGE_NAME_MAP.get(detected_language_code, detected_language_code.title())
    original_subtitle_language = speech_language if speech_language != "Auto detect" else detected_language_name
    output_subtitle_language = original_subtitle_language

    needs_translation = needs_openai_transform(speech_language, target_language)

    if needs_translation:
        status_placeholder.info(f"Translating subtitles to {target_language}...")
        progress_bar.progress(58)
        segments = translate_segments(segments, target_language)
        output_subtitle_language = target_language
    elif target_language != "Original language (no translation)":
        output_subtitle_language = target_language

    status_placeholder.info("Generating subtitle files...")
    progress_bar.progress(76)
    srt_path, vtt_path = write_subtitle_files(segments, output_paths["srt"], output_paths["vtt"])

    captioned_video_path = None
    if should_burn_subtitles:
        if check_ffmpeg():
            status_placeholder.info("Burning subtitles into the final video with FFmpeg...")
            progress_bar.progress(90)
            captioned_video_path = burn_subtitles_into_video(
                video_path,
                srt_path,
                output_paths["captioned_video"],
            )
        else:
            warnings.append("FFmpeg is not installed, so subtitle burn-in was skipped. SRT and VTT files were still generated.")

    progress_bar.progress(100)

    return {
        "video_path": video_path,
        "audio_path": audio_path,
        "srt_path": srt_path,
        "vtt_path": vtt_path,
        "captioned_video_path": captioned_video_path,
        "segments": segments,
        "text": segments_to_plain_text(segments),
        "detected_language": detected_language_name,
        "target_language": target_language,
        "output_subtitle_language": output_subtitle_language,
        "warnings": warnings,
    }


def show_results(result: dict[str, Any]) -> None:
    """Display generated assets, previews, and downloads after processing finishes."""
    for warning in result.get("warnings", []):
        st.warning(warning)

    st.markdown('<div class="status-pill">Captions generated successfully</div>', unsafe_allow_html=True)
    st.balloons()

    render_summary(result)

    before_col, after_col = st.columns(2)
    with before_col:
        st.markdown('<div class="glass-card"><h3>Original Video</h3></div>', unsafe_allow_html=True)
        st.video(str(result["video_path"]))
    with after_col:
        st.markdown('<div class="glass-card"><h3>Captioned Video</h3></div>', unsafe_allow_html=True)
        if result["captioned_video_path"] and result["captioned_video_path"].exists():
            st.video(str(result["captioned_video_path"]))
        else:
            st.info("Caption burn-in was skipped for this run.")

    st.markdown('<div class="glass-card"><h3>Transcript</h3></div>', unsafe_allow_html=True)
    st.text_area("Transcribed text", result["text"], height=200, label_visibility="collapsed")

    st.markdown('<div class="glass-card"><h3>Timestamped Segments</h3></div>', unsafe_allow_html=True)
    rows = [
        {
            "Start": format_timestamp(segment["start"]),
            "End": format_timestamp(segment["end"]),
            "Text": segment["text"],
        }
        for segment in result["segments"]
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    download_col1, download_col2, download_col3 = st.columns(3)
    with download_col1:
        st.download_button(
            "Download SRT",
            data=result["srt_path"].read_bytes(),
            file_name=result["srt_path"].name,
            mime="application/x-subrip",
        )
    with download_col2:
        st.download_button(
            "Download VTT",
            data=result["vtt_path"].read_bytes(),
            file_name=result["vtt_path"].name,
            mime="text/vtt",
        )
    with download_col3:
        if result["captioned_video_path"] and result["captioned_video_path"].exists():
            st.download_button(
                "Download Final Video",
                data=result["captioned_video_path"].read_bytes(),
                file_name=result["captioned_video_path"].name,
                mime="video/mp4",
            )


def main() -> None:
    """Render the Streamlit interface and orchestrate processing."""
    st.set_page_config(
        page_title="AI Video Caption Generator",
        page_icon="AI",
        layout="wide",
    )
    inject_styles()
    render_hero()

    if "result" not in st.session_state:
        st.session_state.result = None

    left_col, right_col = st.columns([1.2, 0.8], gap="large")

    with left_col:
        st.markdown('<div class="glass-card"><h3>Upload & Configure</h3></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload an MP4 video", type=["mp4"])
        speech_language = st.selectbox("Spoken audio language", SPEECH_LANGUAGE_OPTIONS, index=0)
        target_language = st.selectbox("Subtitle language", LANGUAGE_OPTIONS, index=0)
        should_burn_subtitles = st.checkbox("Burn subtitles into the final video", value=True)

        st.markdown(
            """
            <p class="hint">
                Choose the spoken language when you know it for better transcription accuracy.
                Translation uses the OpenAI API only when the subtitle language is different from the spoken language.
            </p>
            """,
            unsafe_allow_html=True,
        )

        if uploaded_file is not None:
            st.markdown('<div class="glass-card"><h3>Upload Preview</h3></div>', unsafe_allow_html=True)
            st.video(uploaded_file)

        generate_clicked = st.button("Generate Captions", type="primary")

        if generate_clicked:
            if uploaded_file is None:
                st.error("Please upload an MP4 video before starting the caption pipeline.")
            elif needs_openai_transform(speech_language, target_language) and not os.getenv("OPENAI_API_KEY"):
                st.error(
                    "This subtitle mode needs the OpenAI API. Set OPENAI_API_KEY, or choose "
                    "'Original language (no translation)' if you want the raw Whisper output."
                )
            else:
                progress_bar = st.progress(0)
                status_placeholder = st.empty()

                try:
                    with st.spinner("Processing your video..."):
                        saved_video = save_uploaded_video(uploaded_file)
                        result = run_pipeline(
                            video_path=saved_video,
                            speech_language=speech_language,
                            target_language=target_language,
                            should_burn_subtitles=should_burn_subtitles,
                            progress_bar=progress_bar,
                            status_placeholder=status_placeholder,
                        )
                    status_placeholder.empty()
                    st.session_state.result = result
                except Exception as exc:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.session_state.result = None
                    st.error(f"Processing failed: {exc}")
                    st.markdown(
                        """
                        <div class="glass-card">
                            <h3>Troubleshooting tips</h3>
                            <p class="hint">
                                Make sure FFmpeg is installed and available on your PATH, your video contains speech,
                                and keep <code>OPENAI_API_KEY</code> set if you selected translated subtitles.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with right_col:
        st.markdown('<div class="glass-card"><h3>Environment Checks</h3></div>', unsafe_allow_html=True)
        ffmpeg_available = check_ffmpeg()
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">FFmpeg status</div>
                <div class="metric-value">{'Available' if ffmpeg_available else 'Not found'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">OpenAI translation key</div>
                <div class="metric-value">{'Configured' if os.getenv('OPENAI_API_KEY') else 'Missing'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="glass-card">
                <h3>Pipeline</h3>
                <p class="hint">1. Upload MP4</p>
                <p class="hint">2. Select the spoken audio language</p>
                <p class="hint">3. Extract WAV audio</p>
                <p class="hint">4. Transcribe with Whisper base</p>
                <p class="hint">5. Optionally translate subtitles</p>
                <p class="hint">6. Export SRT and VTT</p>
                <p class="hint">7. Burn captions into MP4</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.result:
        show_results(st.session_state.result)


if __name__ == "__main__":
    main()
