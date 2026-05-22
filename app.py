from __future__ import annotations

import re
import traceback

import gradio as gr

from mr_maker import make_mr


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def clean_error(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


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
        return f"Failed: {clean_error(str(exc))}\n\n{details}", None


with gr.Blocks(title="Vocal MR Maker") as demo:
    gr.Markdown("# Vocal MR Maker")
    gr.Markdown(
        "Create an instrumental/MR track by extracting MP3 audio from a YouTube URL "
        "or an uploaded audio file. Use only content you have the right to process."
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
