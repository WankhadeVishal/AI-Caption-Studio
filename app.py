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
    """Apply a fully new adaptive design system for both light and dark mode."""
    st.markdown(
        """
        <style>
            :root {
                color-scheme: light;
                --bg-main: #f4f7fb;
                --bg-accent-a: rgba(83, 162, 255, 0.22);
                --bg-accent-b: rgba(255, 148, 110, 0.18);
                --surface: rgba(255, 255, 255, 0.74);
                --surface-strong: rgba(255, 255, 255, 0.92);
                --surface-soft: rgba(244, 248, 255, 0.8);
                --ink: #162033;
                --ink-soft: #5f6c82;
                --ink-faint: #8390a7;
                --line: rgba(22, 32, 51, 0.10);
                --accent: #3e7bfa;
                --accent-2: #16a0b5;
                --accent-3: #ff7d59;
                --success: #15795f;
                --warning: #b46d1c;
                --shadow: 0 20px 55px rgba(32, 49, 79, 0.12);
                --hero-shadow: 0 28px 80px rgba(41, 67, 112, 0.16);
                --button-text: #f8fbff;
            }

            @media (prefers-color-scheme: dark) {
                :root {
                    color-scheme: dark;
                    --bg-main: #0b1220;
                    --bg-accent-a: rgba(62, 123, 250, 0.18);
                    --bg-accent-b: rgba(255, 125, 89, 0.12);
                    --surface: rgba(13, 20, 35, 0.72);
                    --surface-strong: rgba(14, 23, 40, 0.9);
                    --surface-soft: rgba(18, 29, 50, 0.86);
                    --ink: #edf3ff;
                    --ink-soft: #b4c0d7;
                    --ink-faint: #8e9bb4;
                    --line: rgba(255, 255, 255, 0.09);
                    --accent: #6e9bff;
                    --accent-2: #4dd0e1;
                    --accent-3: #ff9b78;
                    --success: #6bf0c6;
                    --warning: #ffcf7d;
                    --shadow: 0 22px 65px rgba(0, 0, 0, 0.34);
                    --hero-shadow: 0 28px 90px rgba(0, 0, 0, 0.38);
                    --button-text: #eff6ff;
                }
            }

            .stApp {
                background:
                    radial-gradient(circle at 10% 14%, var(--bg-accent-a), transparent 24%),
                    radial-gradient(circle at 88% 10%, var(--bg-accent-b), transparent 22%),
                    linear-gradient(135deg, var(--bg-main) 0%, color-mix(in srgb, var(--bg-main) 90%, white 10%) 100%);
                color: var(--ink);
                font-family: "Segoe UI", "Trebuchet MS", sans-serif;
                overflow-x: hidden;
            }

            .stApp::before,
            .stApp::after {
                content: "";
                position: fixed;
                inset: auto;
                pointer-events: none;
                z-index: 0;
                border-radius: 999px;
                filter: blur(14px);
                animation: floatBlob 18s ease-in-out infinite;
            }

            .stApp::before {
                width: 260px;
                height: 260px;
                top: 90px;
                left: -90px;
                background: color-mix(in srgb, var(--accent) 18%, transparent);
            }

            .stApp::after {
                width: 300px;
                height: 300px;
                right: -110px;
                top: 300px;
                background: color-mix(in srgb, var(--accent-3) 16%, transparent);
                animation-delay: -6s;
            }

            @keyframes floatBlob {
                0% { transform: translateY(0px) scale(1); }
                50% { transform: translateY(-28px) scale(1.05); }
                100% { transform: translateY(0px) scale(1); }
            }

            .block-container {
                padding-top: 3rem;
                padding-bottom: 2.8rem;
                max-width: 1240px;
                position: relative;
                z-index: 1;
            }

            h1, h2, h3 {
                color: var(--ink);
                font-family: "Cambria", "Georgia", serif;
                letter-spacing: 0.01em;
            }

            .hero-card,
            .glass-card,
            div[data-testid="stFileUploader"],
            div[data-testid="stMetric"],
            div[data-testid="stDataFrame"],
            div[data-testid="stAlert"] {
                background: rgba(255, 255, 255, 0.76);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--line);
                border-radius: 24px;
                box-shadow: var(--shadow);
                animation: riseIn 0.9s ease both;
            }

            .hero-card {
                padding: 2rem;
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
                background:
                    linear-gradient(135deg, var(--surface-strong), color-mix(in srgb, var(--surface-strong) 92%, var(--accent) 8%)),
                    linear-gradient(120deg, color-mix(in srgb, var(--accent-2) 10%, transparent), color-mix(in srgb, var(--accent-3) 8%, transparent));
                box-shadow: var(--hero-shadow);
            }

            .hero-grid {
                display: grid;
                grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.9fr);
                gap: 1.5rem;
                align-items: stretch;
            }

            .hero-card::after {
                content: "";
                position: absolute;
                inset: auto -42px -42px auto;
                width: 180px;
                height: 180px;
                border-radius: 999px;
                background: radial-gradient(circle, color-mix(in srgb, var(--accent-2) 22%, transparent), transparent 70%);
                pointer-events: none;
                animation: pulseHalo 8s ease-in-out infinite;
            }

            .hero-card::before {
                content: "";
                position: absolute;
                top: -30%;
                right: 14%;
                width: 180px;
                height: 180px;
                background: radial-gradient(circle, color-mix(in srgb, var(--accent-3) 16%, transparent), transparent 68%);
                border-radius: 999px;
                pointer-events: none;
                animation: drift 14s linear infinite;
            }

            .glass-card {
                padding: 1.15rem 1.2rem;
                margin-bottom: 1rem;
            }

            div[data-testid="stFileUploader"] {
                padding: 0.85rem;
                background:
                    linear-gradient(180deg, color-mix(in srgb, var(--surface-strong) 96%, transparent), color-mix(in srgb, var(--surface) 92%, transparent));
                box-shadow: 0 18px 40px color-mix(in srgb, var(--accent) 10%, transparent);
            }

            div[data-testid="stFileUploader"] > label {
                color: var(--ink) !important;
                font-size: 1rem !important;
                font-weight: 700 !important;
                margin-bottom: 0.55rem !important;
            }

            div[data-testid="stFileUploader"] section {
                min-height: 112px;
                border-radius: 22px !important;
                border: 1.5px dashed color-mix(in srgb, var(--accent) 34%, transparent) !important;
                background:
                    linear-gradient(135deg, color-mix(in srgb, var(--surface-soft) 88%, transparent), color-mix(in srgb, var(--surface-strong) 94%, transparent)) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.35);
            }

            div[data-testid="stFileUploader"] section:hover {
                transform: translateY(-1px);
                border-color: color-mix(in srgb, var(--accent-2) 46%, transparent) !important;
                box-shadow: 0 14px 28px color-mix(in srgb, var(--accent-2) 10%, transparent);
            }

            div[data-testid="stFileUploader"] section button {
                border-radius: 14px !important;
                border: 1px solid color-mix(in srgb, var(--accent) 24%, transparent) !important;
                background: linear-gradient(135deg, color-mix(in srgb, var(--surface-strong) 96%, transparent), color-mix(in srgb, var(--surface-soft) 96%, transparent)) !important;
                color: var(--ink) !important;
                font-weight: 700 !important;
            }

            div[data-testid="stFileUploader"] small,
            div[data-testid="stFileUploader"] span,
            div[data-testid="stFileUploader"] p {
                color: var(--ink-soft) !important;
            }

            .eyebrow {
                color: var(--accent-3);
                text-transform: uppercase;
                letter-spacing: 0.24em;
                font-size: 0.75rem;
                margin-bottom: 0.78rem;
                font-weight: 900;
                animation: fadeSlide 0.9s ease both;
            }

            .hero-title {
                font-size: clamp(2.7rem, 5vw, 4.7rem);
                line-height: 0.95;
                margin: 0 0 0.95rem 0;
                max-width: 780px;
                font-weight: 800;
                animation: fadeSlide 1.05s ease both;
            }

            .hero-subtitle {
                color: var(--ink-soft);
                font-size: 1.03rem;
                max-width: 700px;
                margin: 0;
                animation: fadeSlide 1.2s ease both;
            }

            .chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.7rem;
                margin-top: 1.2rem;
                animation: fadeSlide 1.35s ease both;
            }

            .chip {
                padding: 0.56rem 0.92rem;
                border-radius: 999px;
                background: color-mix(in srgb, var(--surface-soft) 70%, transparent);
                border: 1px solid color-mix(in srgb, var(--line) 88%, transparent);
                color: var(--ink);
                font-size: 0.86rem;
                letter-spacing: 0.02em;
                position: relative;
                overflow: hidden;
            }

            .chip::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(120deg, transparent, rgba(255,255,255,0.45), transparent);
                transform: translateX(-140%);
                animation: sheen 7s linear infinite;
            }

            .hero-stack {
                background:
                    linear-gradient(180deg, color-mix(in srgb, var(--surface-strong) 84%, var(--accent) 16%), color-mix(in srgb, var(--surface-soft) 86%, var(--accent-2) 14%));
                border: 1px solid var(--line);
                border-radius: 22px;
                padding: 1.1rem;
                position: relative;
                overflow: hidden;
                animation: riseIn 1.05s ease both;
            }

            .hero-stack::before {
                content: "";
                position: absolute;
                inset: auto -35px -35px auto;
                width: 140px;
                height: 140px;
                border-radius: 999px;
                background: radial-gradient(circle, color-mix(in srgb, var(--accent-3) 20%, transparent), transparent 68%);
                pointer-events: none;
                animation: pulseHalo 7s ease-in-out infinite;
            }

            .stack-label {
                color: var(--ink-faint);
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.18em;
                margin-bottom: 0.75rem;
            }

            .stack-item {
                display: grid;
                grid-template-columns: 42px 1fr;
                gap: 0.75rem;
                padding: 0.72rem 0;
                border-bottom: 1px solid var(--line);
            }

            .stack-item:last-child {
                border-bottom: none;
            }

            .stack-num {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                color: var(--button-text);
                background: linear-gradient(135deg, var(--accent), var(--accent-3));
                animation: bob 4s ease-in-out infinite;
            }

            .stack-title {
                color: var(--ink);
                font-size: 0.98rem;
                font-weight: 700;
                margin-bottom: 0.15rem;
            }

            .stack-copy {
                color: var(--ink-soft);
                font-size: 0.88rem;
                line-height: 1.45;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.9rem 1.05rem;
                border-radius: 18px;
                background: rgba(45, 123, 89, 0.08);
                border: 1px solid rgba(45, 123, 89, 0.18);
                color: var(--success);
                font-weight: 700;
                animation: pulseGlow 1.8s ease-in-out infinite;
            }

            @keyframes pulseGlow {
                0% { box-shadow: 0 0 0 0 rgba(112, 201, 176, 0.22); }
                70% { box-shadow: 0 0 0 16px rgba(112, 201, 176, 0); }
                100% { box-shadow: 0 0 0 0 rgba(107, 247, 177, 0); }
            }

            @keyframes pulseHalo {
                0% { transform: scale(1); opacity: 0.9; }
                50% { transform: scale(1.08); opacity: 0.5; }
                100% { transform: scale(1); opacity: 0.9; }
            }

            @keyframes drift {
                0% { transform: translate(0px, 0px) rotate(0deg); }
                50% { transform: translate(12px, 18px) rotate(18deg); }
                100% { transform: translate(0px, 0px) rotate(0deg); }
            }

            @keyframes riseIn {
                0% { opacity: 0; transform: translateY(24px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes fadeSlide {
                0% { opacity: 0; transform: translateY(18px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes sheen {
                0% { transform: translateX(-140%); }
                20% { transform: translateX(140%); }
                100% { transform: translateX(140%); }
            }

            @keyframes bob {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-4px); }
                100% { transform: translateY(0px); }
            }

            .metric-label {
                color: var(--ink-soft);
                margin-bottom: 0.35rem;
                font-size: 0.82rem;
                letter-spacing: 0.14em;
                text-transform: uppercase;
            }

            .metric-value {
                font-size: 1.28rem;
                font-weight: 700;
                color: var(--ink);
            }

            .hint {
                color: var(--ink-soft);
                font-size: 0.92rem;
                line-height: 1.6;
                margin-top: 0.3rem;
                margin-bottom: 1.2rem;
            }

            .section-shell {
                padding: 1.1rem 1.2rem;
                margin-bottom: 1rem;
                border-radius: 24px;
                background: linear-gradient(180deg, var(--surface-strong), var(--surface));
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                position: relative;
                overflow: hidden;
                animation: riseIn 0.9s ease both;
            }

            .section-shell::before {
                content: "";
                position: absolute;
                inset: 0 auto 0 0;
                width: 10px;
                background: linear-gradient(180deg, var(--accent-3), var(--accent), var(--accent-2));
            }

            .section-kicker {
                color: var(--accent-3);
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.22em;
                margin-bottom: 0.4rem;
                padding-left: 0.4rem;
            }

            .section-title {
                margin: 0;
                font-size: 1.7rem;
                padding-left: 0.4rem;
            }

            .section-copy {
                margin: 0.4rem 0 0 0;
                color: var(--ink-soft);
                max-width: 640px;
                padding-left: 0.4rem;
            }

            .ops-board {
                padding: 1.15rem 1.2rem;
                border-radius: 24px;
                background:
                    radial-gradient(circle at top right, color-mix(in srgb, var(--accent-3) 16%, transparent), transparent 24%),
                    linear-gradient(180deg, color-mix(in srgb, var(--surface-strong) 65%, var(--accent) 35%), color-mix(in srgb, var(--surface-soft) 78%, var(--accent-2) 22%));
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                animation: riseIn 1.05s ease both;
            }

            .ops-row {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 0.8rem;
                align-items: center;
                padding: 0.85rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.09);
            }

            .ops-row:last-child {
                border-bottom: none;
            }

            .ops-label {
                color: var(--ink-faint);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                margin-bottom: 0.2rem;
            }

            .ops-board .section-kicker {
                color: var(--accent-3);
                padding-left: 0;
            }

            .ops-board .section-title {
                color: var(--ink);
                padding-left: 0;
            }

            .ops-board .section-copy {
                color: var(--ink-soft);
                padding-left: 0;
            }

            .ops-value {
                font-size: 1rem;
                font-weight: 700;
                color: var(--ink);
            }

            .ops-state {
                padding: 0.4rem 0.75rem;
                border-radius: 999px;
                border: 1px solid var(--line);
                background: rgba(255, 255, 255, 0.18);
                color: var(--ink);
                font-size: 0.84rem;
                font-weight: 700;
            }

            .ops-state.good {
                color: var(--success);
                border-color: rgba(143, 247, 194, 0.25);
                background: rgba(143, 247, 194, 0.08);
            }

            .ops-state.warn {
                color: var(--warning);
                border-color: rgba(255, 210, 125, 0.28);
                background: rgba(255, 210, 125, 0.08);
            }

            .pipeline-card {
                padding: 1.15rem 1.2rem;
                border-radius: 24px;
                margin-top: 1rem;
                background: linear-gradient(180deg, var(--surface-strong), var(--surface));
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                animation: riseIn 1.18s ease both;
            }

            .pipeline-step {
                display: grid;
                grid-template-columns: 34px 1fr;
                gap: 0.8rem;
                padding: 0.7rem 0;
                align-items: start;
            }

            .pipeline-index {
                width: 34px;
                height: 34px;
                border-radius: 12px;
                background: color-mix(in srgb, var(--accent) 10%, transparent);
                border: 1px solid color-mix(in srgb, var(--accent) 20%, transparent);
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--accent);
                font-weight: 800;
                font-size: 0.88rem;
            }

            .pipeline-copy {
                color: var(--ink-soft);
                font-size: 0.95rem;
                line-height: 1.45;
            }

            .stButton > button,
            .stDownloadButton > button {
                width: 100%;
                border-radius: 18px;
                border: 1px solid color-mix(in srgb, var(--accent) 22%, transparent);
                background: linear-gradient(135deg, var(--accent), var(--accent-2));
                color: var(--button-text);
                font-weight: 700;
                min-height: 3rem;
                box-shadow: 0 14px 26px color-mix(in srgb, var(--accent) 18%, transparent);
                position: relative;
                overflow: hidden;
            }

            .stButton > button {
                max-width: 250px;
                font-size: 1.02rem;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: color-mix(in srgb, var(--accent) 36%, transparent);
                transform: translateY(-2px);
            }

            .stButton > button::after,
            .stDownloadButton > button::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(120deg, transparent, rgba(255,255,255,0.26), transparent);
                transform: translateX(-150%);
                animation: sheen 5.5s linear infinite;
            }

            .stProgress > div > div {
                background: linear-gradient(90deg, var(--accent), var(--accent-2), var(--accent-3));
            }

            .stSelectbox label,
            .stCheckbox label,
            .stFileUploader label {
                color: var(--ink) !important;
                font-weight: 600;
            }

            .stSelectbox label {
                font-size: 0.92rem !important;
                margin-bottom: 0.35rem !important;
            }

            .stSelectbox div[data-baseweb="select"] > div {
                background: color-mix(in srgb, var(--surface-strong) 92%, transparent);
                border-radius: 18px;
                border: 1px solid var(--line);
                min-height: 54px;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.28);
                transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
            }

            .stSelectbox div[data-baseweb="select"] > div:hover {
                border-color: color-mix(in srgb, var(--accent) 28%, transparent);
                transform: translateY(-1px);
                box-shadow: 0 12px 24px color-mix(in srgb, var(--accent) 10%, transparent);
            }

            .stSelectbox div[data-baseweb="select"] * {
                color: var(--ink) !important;
            }

            div[data-testid="stCheckbox"] {
                padding-top: 1.95rem;
            }

            .stCheckbox > label {
                background: color-mix(in srgb, var(--surface-strong) 94%, transparent);
                border-radius: 18px;
                border: 1px solid var(--line);
                padding: 0.78rem 0.95rem;
                min-height: 54px;
                display: flex !important;
                align-items: center;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.22);
            }

            .stCheckbox p {
                color: var(--ink) !important;
                font-weight: 600 !important;
            }

            div[data-testid="stTextArea"] textarea {
                background: color-mix(in srgb, var(--surface-strong) 92%, transparent) !important;
                color: var(--ink) !important;
                border: 1px solid var(--line) !important;
                border-radius: 20px !important;
            }

            div[data-testid="stDataFrame"] {
                overflow: hidden;
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-top: 2.1rem;
                }

                .hero-card {
                    padding: 1.35rem;
                }

                .hero-grid {
                    grid-template-columns: 1fr;
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
    """Render a new editorial-style project header."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">AI Caption Studio</div>
                    <h1 class="hero-title">Turn raw video into polished subtitles and a presentation-ready final export.</h1>
                    <p class="hero-subtitle">
                        Designed for project demonstrations, this workspace turns video into a clear transcript,
                        downloadable subtitle assets, and a final captioned export through a refined, animated interface.
                    </p>
                    <div class="chip-row">
                        <div class="chip">Python</div>
                        <div class="chip">Streamlit</div>
                        <div class="chip">OpenAI Whisper</div>
                        <div class="chip">MoviePy</div>
                        <div class="chip">FFmpeg</div>
                        <div class="chip">OpenAI API</div>
                        <div class="chip">SRT</div>
                    </div>
                </div>
                <div class="hero-stack">
                    <div class="stack-label">Workflow Snapshot</div>
                    <div class="stack-item">
                        <div class="stack-num">01</div>
                        <div>
                            <div class="stack-title">Video to Audio</div>
                            <div class="stack-copy">The app takes audio from the uploaded video.</div>
                        </div>
                    </div>
                    <div class="stack-item">
                        <div class="stack-num">02</div>
                        <div>
                            <div class="stack-title">Audio to Subtitles</div>
                            <div class="stack-copy">Whisper turns speech into subtitle lines with timestamps.</div>
                        </div>
                    </div>
                    <div class="stack-item">
                        <div class="stack-num">03</div>
                        <div>
                            <div class="stack-title">Final Output</div>
                            <div class="stack-copy">You get subtitle files and a final video with captions.</div>
                        </div>
                    </div>
                </div>
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
        st.markdown(
            '<div class="section-shell"><div class="section-kicker">Preview A</div><h3 class="section-title">Original Video</h3></div>',
            unsafe_allow_html=True,
        )
        st.video(str(result["video_path"]))
    with after_col:
        st.markdown(
            '<div class="section-shell"><div class="section-kicker">Preview B</div><h3 class="section-title">Captioned Video</h3></div>',
            unsafe_allow_html=True,
        )
        if result["captioned_video_path"] and result["captioned_video_path"].exists():
            st.video(str(result["captioned_video_path"]))
        else:
            st.info("Caption burn-in was skipped for this run.")

    st.markdown(
        '<div class="section-shell"><div class="section-kicker">Transcript</div><h3 class="section-title">Spoken Content</h3><p class="section-copy">Review the generated transcript before exporting or embedding subtitles.</p></div>',
        unsafe_allow_html=True,
    )
    st.text_area("Transcribed text", result["text"], height=200, label_visibility="collapsed")

    st.markdown(
        '<div class="section-shell"><div class="section-kicker">Timeline</div><h3 class="section-title">Timestamped Segments</h3><p class="section-copy">Each caption cue is organized with precise start and end times.</p></div>',
        unsafe_allow_html=True,
    )
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

    st.markdown(
        """
        <div class="section-shell">
            <div class="section-kicker">Workspace</div>
            <h3 class="section-title">Upload & Configure</h3>
            <p class="section-copy">Set the language flow, preview the source clip, and launch the subtitle pipeline from one clean workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload an MP4 video", type=["mp4"])
    controls_col1, controls_col2, controls_col3 = st.columns([1, 1, 1])
    with controls_col1:
        speech_language = st.selectbox("Spoken audio language", SPEECH_LANGUAGE_OPTIONS, index=0)
    with controls_col2:
        target_language = st.selectbox("Subtitle language", LANGUAGE_OPTIONS, index=0)
    with controls_col3:
        should_burn_subtitles = st.checkbox("Add subtitles into the final video", value=True)

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
        st.markdown(
            '<div class="section-shell"><div class="section-kicker">Source</div><h3 class="section-title">Upload Preview</h3></div>',
            unsafe_allow_html=True,
        )
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

    if st.session_state.result:
        show_results(st.session_state.result)


if __name__ == "__main__":
    main()
