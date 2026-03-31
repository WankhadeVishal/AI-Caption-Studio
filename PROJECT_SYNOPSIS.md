# Project Synopsis

## Title
AI-Powered Video Caption Generator

## Introduction
The AI-Powered Video Caption Generator is a full-stack web application developed to automate the process of generating subtitles for video content. The system accepts an MP4 video as input, extracts its audio, transcribes spoken content using OpenAI Whisper, optionally translates the subtitles into another language, generates subtitle files in SRT and VTT formats, and burns subtitles directly into the video using FFmpeg. The application is designed with a modern Streamlit-based user interface to provide a clean, interactive, and user-friendly experience.

In the current digital era, video content is widely used for education, entertainment, marketing, and communication. However, manually creating captions is time-consuming and error-prone. This project addresses that challenge by offering an automated and modular solution that improves accessibility, usability, and content reach.

## Problem Statement
Creating captions for videos manually requires significant time and effort, especially for long-form content. Many small creators, students, and professionals lack access to affordable tools for subtitle generation and video caption embedding. There is a need for a lightweight and efficient application that can automatically generate subtitle files and produce captioned videos through an easy web interface.

## Objectives
- To build a web application that accepts MP4 video uploads.
- To extract audio from uploaded videos automatically.
- To transcribe spoken content using OpenAI Whisper.
- To generate timestamp-based subtitle files in SRT and VTT formats.
- To optionally translate subtitles into another language using the OpenAI API.
- To burn subtitles into the final video using FFmpeg.
- To provide a modern Streamlit UI with previews, progress indicators, and download options.

## Scope of the Project
This project focuses on local video caption generation for desktop users. It supports:
- MP4 video upload and preview
- Audio extraction from the uploaded video
- Whisper-based speech-to-text transcription
- Subtitle generation in standard formats
- Subtitle translation for selected languages
- Subtitle burn-in to create a final captioned MP4
- Download of generated subtitle files and processed videos

The system is suitable for educational demonstrations, prototype deployments, student mini-projects, and small-scale content automation tasks.

## Proposed Solution
The proposed solution is a modular Python application built with Streamlit on the frontend and utility modules on the backend. The system processes a video in multiple stages. First, the user uploads a video file through the Streamlit interface. The application then extracts audio from the video and converts it to WAV format. The audio is transcribed using the Whisper model. The resulting transcript is converted into timestamped subtitle segments, which are then exported into SRT and VTT files. If the user selects a target language different from the spoken language, the subtitles are translated through the OpenAI API. Finally, FFmpeg is used to embed subtitles into the video, and the user can preview and download the final outputs.

## Technology Stack
- Python 3.10+
- Streamlit for frontend user interface
- OpenAI Whisper for speech-to-text transcription
- MoviePy for audio extraction
- FFmpeg for subtitle burn-in and video processing
- `srt` library for subtitle formatting
- OpenAI API for optional subtitle translation

## System Modules

### 1. User Interface Module
The Streamlit interface handles video upload, language selection, preview display, progress tracking, and file downloads. It offers a responsive and visually modern layout.

### 2. Audio Extraction Module
This module extracts audio from the uploaded video and stores it as a WAV file suitable for speech recognition.

### 3. Transcription Module
The transcription module uses the Whisper model to identify speech and generate text with timestamps. It outputs structured subtitle segments.

### 4. Subtitle Generation Module
This module converts transcript segments into subtitle files in SRT and VTT formats. These files are compatible with standard video players and editing tools.

### 5. Translation Module
The translation module uses the OpenAI API to convert subtitle text into another language when required by the user.

### 6. Subtitle Burn-In Module
The burn-in module uses FFmpeg to embed subtitle text directly into the video and produce a final captioned MP4 file.

## Working Methodology
The application follows the workflow below:

1. User uploads an MP4 video.
2. Video is stored in the `uploads` directory.
3. Audio is extracted and saved in WAV format.
4. Whisper transcribes the audio into timestamped text segments.
5. Subtitle files are generated in SRT and VTT formats.
6. If selected, subtitles are translated into the target language.
7. FFmpeg burns subtitles into the final video.
8. The UI displays transcript text, subtitle previews, and download options.

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

## Key Features
- Automated subtitle generation from video speech
- Subtitle export in SRT and VTT formats
- Optional translation to other languages
- Subtitle burn-in using FFmpeg
- Original and processed video previews
- Timestamp display for transcription segments
- Download support for subtitle files and final video
- Modular backend for clean code maintenance

## Advantages
- Reduces manual effort in subtitle creation
- Improves video accessibility and viewer engagement
- Supports reuse of subtitles across different video platforms
- Provides a user-friendly interface for non-technical users
- Uses modular design for easy future extension

## Limitations
- Accuracy depends on audio clarity and background noise levels
- Translation quality depends on API availability and model performance
- FFmpeg must be installed locally for subtitle burn-in
- Large video files may require more processing time and system resources

## Future Enhancements
- Support for additional video formats beyond MP4
- More translation options and language presets
- Batch processing for multiple videos
- Cloud storage integration
- Editable subtitle correction interface
- Speaker diarization and enhanced subtitle styling

## Expected Outcome
The expected outcome of this project is a fully functional application that simplifies subtitle generation for videos. Users will be able to upload a video, automatically generate captions, export subtitle files, optionally translate them, and download a final subtitle-burned version of the video. The project demonstrates practical use of AI, multimedia processing, and web-based interaction in a real-world productivity tool.

## Conclusion
The AI-Powered Video Caption Generator is a practical and impactful solution for automating caption creation. By combining Whisper, Streamlit, MoviePy, FFmpeg, and OpenAI services, the application provides an efficient end-to-end workflow for subtitle generation and video enhancement. The project is valuable as a mini-project because it demonstrates integration of artificial intelligence, multimedia processing, and modern web application development in a single cohesive system.
