from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from yt_dlp import YoutubeDL


BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
SEPARATED_DIR = BASE_DIR / "separated"
OUTPUT_DIR = BASE_DIR / "outputs"


@dataclass(frozen=True)
class MrResult:
    title: str
    source_audio: Path
    instrumental: Path


def _ensure_dirs() -> None:
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    SEPARATED_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def download_audio(url: str) -> tuple[str, Path]:
    _ensure_dirs()
    output_template = str(DOWNLOAD_DIR / "%(title).180B [%(id)s].%(ext)s")
    options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
        "quiet": False,
        "restrictfilenames": True,
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        prepared = Path(ydl.prepare_filename(info))
        wav_path = prepared.with_suffix(".wav")

    if not wav_path.exists():
        raise FileNotFoundError(f"Downloaded audio was not found: {wav_path}")

    return info.get("title", wav_path.stem), wav_path


def separate_vocals(audio_path: Path, model: str = "htdemucs") -> Path:
    _ensure_dirs()
    command = [
        "python",
        "-m",
        "demucs",
        "--two-stems",
        "vocals",
        "-n",
        model,
        "-o",
        str(SEPARATED_DIR),
        str(audio_path),
    ]
    subprocess.run(command, check=True)

    instrumental = SEPARATED_DIR / model / audio_path.stem / "no_vocals.wav"
    if not instrumental.exists():
        raise FileNotFoundError(f"Demucs output was not found: {instrumental}")

    final_path = OUTPUT_DIR / f"{audio_path.stem}_MR.wav"
    shutil.copy2(instrumental, final_path)
    return final_path


def make_mr(url: str, model: str = "htdemucs") -> MrResult:
    title, audio_path = download_audio(url)
    instrumental = separate_vocals(audio_path, model=model)
    return MrResult(title=title, source_audio=audio_path, instrumental=instrumental)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create MR/instrumental audio from a YouTube URL.")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--model", default="htdemucs", help="Demucs model name")
    args = parser.parse_args()

    result = make_mr(args.url, model=args.model)
    print(f"Title: {result.title}")
    print(f"Source audio: {result.source_audio}")
    print(f"MR file: {result.instrumental}")


if __name__ == "__main__":
    main()
