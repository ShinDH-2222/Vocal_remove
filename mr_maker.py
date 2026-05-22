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


def download_audio(
    url: str,
    cookies_file: str | None = None,
    cookies_browser: str | None = None,
) -> tuple[str, Path]:
    _ensure_dirs()
    output_template = str(DOWNLOAD_DIR / "%(title).180B [%(id)s].%(ext)s")
    options = {
        "format": "ba/b/bv*+ba/best",
        "format_sort": ["hasaud", "abr", "res:720"],
        "outtmpl": output_template,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
        "restrictfilenames": True,
    }
    if cookies_file:
        options["cookiefile"] = cookies_file
    if cookies_browser:
        options["cookiesfrombrowser"] = (cookies_browser,)

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        requested_downloads = info.get("requested_downloads") or []
        if requested_downloads:
            audio_path = Path(requested_downloads[0]["filepath"]).with_suffix(".mp3")
        else:
            prepared = Path(ydl.prepare_filename(info))
            audio_path = prepared.with_suffix(".mp3")

    if not audio_path.exists():
        raise FileNotFoundError(f"Downloaded audio was not found: {audio_path}")

    return info.get("title", audio_path.stem), audio_path


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


def prepare_uploaded_audio(upload_path: str) -> tuple[str, Path]:
    _ensure_dirs()
    source = Path(upload_path)
    if not source.exists():
        raise FileNotFoundError(f"Uploaded audio was not found: {source}")

    target = DOWNLOAD_DIR / source.name
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target.stem, target


def make_mr(
    url: str | None = None,
    model: str = "htdemucs",
    cookies_file: str | None = None,
    cookies_browser: str | None = None,
    upload_path: str | None = None,
) -> MrResult:
    if upload_path:
        title, audio_path = prepare_uploaded_audio(upload_path)
    elif url:
        title, audio_path = download_audio(
            url,
            cookies_file=cookies_file,
            cookies_browser=cookies_browser,
        )
    else:
        raise ValueError("Provide a YouTube URL or upload an audio file.")

    instrumental = separate_vocals(audio_path, model=model)
    return MrResult(title=title, source_audio=audio_path, instrumental=instrumental)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create MR/instrumental audio from a YouTube URL.")
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument("--cookies", help="Path to a Netscape cookies.txt file for yt-dlp")
    parser.add_argument(
        "--cookies-from-browser",
        choices=["chrome", "edge", "firefox", "brave", "vivaldi", "whale"],
        help="Read YouTube cookies from a local browser profile",
    )
    parser.add_argument("--input", help="Local audio file to process instead of a YouTube URL")
    parser.add_argument("--model", default="htdemucs", help="Demucs model name")
    args = parser.parse_args()

    result = make_mr(
        args.url,
        model=args.model,
        cookies_file=args.cookies,
        cookies_browser=args.cookies_from_browser,
        upload_path=args.input,
    )
    print(f"Title: {result.title}")
    print(f"Source audio: {result.source_audio}")
    print(f"MR file: {result.instrumental}")


if __name__ == "__main__":
    main()
