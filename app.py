from __future__ import annotations

import re
import traceback

import gradio as gr

from mr_maker import make_mr


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def clean_error(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


def friendly_error(exc: Exception, details: str) -> str:
    message = clean_error(str(exc))
    lower_details = details.lower()

    if "could not copy chrome cookie database" in lower_details:
        return (
            "Failed: Chrome cookies could not be read.\n\n"
            "Try one of these:\n"
            "1. Close every Chrome window, including background Chrome processes, then run again.\n"
            "2. Select edge or firefox if you are logged in to YouTube there.\n"
            "3. Export YouTube cookies as cookies.txt and upload that file instead.\n\n"
            f"Original error: {message}"
        )

    if "failed to decrypt with dpapi" in lower_details:
        return (
            "Failed: Browser cookies could not be decrypted by Windows DPAPI.\n\n"
            "This often happens with Chrome/Edge cookies on Windows. Try one of these:\n"
            "1. Log in to YouTube with Firefox, then select firefox in this app.\n"
            "2. Export YouTube cookies as cookies.txt and upload that file.\n"
            "3. Run this app from the same normal Windows user session that owns the browser profile.\n\n"
            f"Original error: {message}"
        )

    if "sign in to confirm" in lower_details or "not a bot" in lower_details:
        return (
            "Failed: YouTube is asking for sign-in or bot verification.\n\n"
            "Use cookies from a browser where YouTube is already logged in, "
            "or upload a valid cookies.txt file.\n\n"
            f"Original error: {message}"
        )

    if "requested format is not available" in lower_details:
        return (
            "Failed: YouTube did not provide a downloadable audio/video format for this request.\n\n"
            "Try again with Firefox cookies or an exported cookies.txt file. "
            "If only this video fails, test a different YouTube video because some videos restrict available formats.\n\n"
            f"Original error: {message}"
        )

    return f"Failed: {message}\n\n{details}"


def create_mr(
    url: str,
    audio_file: str | None,
    cookies_file: str | None,
    cookies_browser: str,
    model: str,
) -> tuple[str, str | None]:
    url = (url or "").strip()
    browser = None if cookies_browser == "None" else cookies_browser

    if not url and not audio_file:
        return "Enter a YouTube URL or upload an audio file.", None

    try:
        result = make_mr(
            url=url or None,
            upload_path=audio_file,
            cookies_file=cookies_file,
            cookies_browser=browser,
            model=model,
        )
        message = (
            f"Done: {result.title}\n"
            f"Source audio: {result.source_audio}\n"
            f"MR file: {result.instrumental}"
        )
        return message, str(result.instrumental)
    except Exception as exc:
        details = clean_error(traceback.format_exc())
        return friendly_error(exc, details), None


with gr.Blocks(title="Vocal MR Maker") as demo:
    gr.Markdown("# Vocal MR Maker")
    gr.Markdown(
        "Create an instrumental/MR track by extracting MP3 audio from a YouTube URL "
        "or an uploaded audio file. Use only content you have the right to process."
    )
    gr.Markdown(
        "If YouTube blocks the request, Firefox cookies or an exported cookies.txt file are usually the most reliable."
    )

    url_input = gr.Textbox(
        label="YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )
    audio_input = gr.Audio(
        label="Or upload audio",
        sources=["upload"],
        type="filepath",
    )
    cookies_input = gr.File(
        label="Optional YouTube cookies.txt",
        file_types=[".txt"],
        type="filepath",
    )
    browser_input = gr.Dropdown(
        label="Use cookies from local browser",
        choices=["None", "chrome", "edge", "firefox", "brave", "vivaldi", "whale"],
        value="None",
    )
    model_input = gr.Dropdown(
        label="Demucs model",
        choices=["mdx_extra_q", "htdemucs", "htdemucs_ft"],
        value="htdemucs",
    )

    run_button = gr.Button("Create MR", variant="primary")
    status_output = gr.Textbox(label="Status", lines=8)
    audio_output = gr.Audio(label="MR preview/download", type="filepath")

    run_button.click(
        fn=create_mr,
        inputs=[url_input, audio_input, cookies_input, browser_input, model_input],
        outputs=[status_output, audio_output],
    )


if __name__ == "__main__":
    demo.launch()
