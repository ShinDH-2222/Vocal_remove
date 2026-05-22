# Vocal MR Maker

Create an instrumental/MR track by extracting audio from a YouTube URL or an uploaded audio file, then removing vocals with Demucs.

## Requirements

- Python 3.10+
- FFmpeg
- Deno, required by recent yt-dlp YouTube challenge solving
- SoundFile, used by torchaudio/Demucs to save separated WAV files

Install Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install Deno on Windows:

```powershell
winget install DenoLand.Deno
```

After installing Deno, close and reopen PowerShell so the updated PATH is loaded.

Check that Deno is available:

```powershell
deno --version
```

## Run The Web App

```powershell
python app.py
```

Open the local URL shown in the terminal.

If YouTube blocks the request:

1. Log in to YouTube in Firefox.
2. Close and reopen PowerShell after installing Deno.
3. Export Firefox cookies to `cookies.txt`, or select `firefox` in the app.
4. If browser cookie reading fails, upload `cookies.txt` in the app.

## CLI Usage

YouTube URL:

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

YouTube URL with cookies file:

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies cookies.txt
```

YouTube URL with Firefox cookies:

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies-from-browser firefox
```

Local audio file:

```powershell
python mr_maker.py --input ".\song.wav"
```

## Troubleshooting

### Sign in to confirm you are not a bot

Use Firefox cookies or upload a valid `cookies.txt` file.

### Could not copy Chrome cookie database

Close all Chrome windows and end remaining `chrome.exe` processes. Firefox is usually more reliable for this workflow.

### Failed to decrypt with DPAPI

Chrome/Edge cookies may fail to decrypt on Windows. Use Firefox or export cookies to `cookies.txt`.

### Requested format is not available

Update yt-dlp, install `yt-dlp[default]`, install Deno, reopen PowerShell, then retry:

```powershell
python -m pip install -U "yt-dlp[default]"
deno --version
yt-dlp --cookies cookies.txt --list-formats "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Demucs cannot save vocals.wav or no_vocals.wav

Install SoundFile, then retry:

```powershell
python -m pip install -U soundfile
```

## Safety

Only process content that you have the rights to use. Do not commit or share `cookies.txt`.
