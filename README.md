# AI Video Caption Generator

A full-stack Streamlit app that uploads an MP4, extracts audio, transcribes speech with Whisper, optionally translates subtitle text with OpenAI, generates `.srt` and `.vtt` files, and burns subtitles into the final video with FFmpeg.

## Features

- Upload MP4 videos from a Streamlit interface
- Extract mono WAV audio for transcription
- Transcribe speech with the Whisper `base` model
- Optionally translate subtitles into another language
- Export subtitle files in SRT and VTT formats
- Burn subtitles directly into the final MP4 using FFmpeg
- Preview the original and captioned videos in the UI
- Review timestamped transcript segments before downloading assets

## Project Structure

```text
video-caption-generator/
|
|-- app.py
|-- utils/
|   |-- __init__.py
|   |-- extract_audio.py
|   |-- transcribe.py
|   |-- generate_subtitles.py
|   |-- translate.py
|   `-- burn_subtitles.py
|-- uploads/
|-- outputs/
|-- requirements.txt
`-- README.md
```

## Requirements

- Python 3.10+
- FFmpeg installed and available on your system `PATH`

## Setup

1. Create and activate a virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: configure translation support by setting your OpenAI API key.

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

4. Start the app:

```bash
streamlit run app.py
```

## Notes for Windows

- Ensure `ffmpeg.exe` is available on your `PATH`.
- The app uses `Path` objects and Windows-safe FFmpeg subtitle path escaping.
- Whisper transcription runs with `fp16=False` for broader CPU compatibility.

## Processing Flow

1. Upload an MP4 file
2. Extract audio to WAV
3. Transcribe with Whisper
4. Optionally translate subtitle text
5. Generate `.srt` and `.vtt`
6. Burn subtitles into a final MP4

## Troubleshooting

- If subtitle burn-in fails, verify that FFmpeg is installed and callable from the terminal.
- If translation fails, ensure `OPENAI_API_KEY` is set before launching Streamlit.
- If Whisper detects no speech, try a video with clearer spoken audio.
# Ai-powered-video-caption-generator
