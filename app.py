from __future__ import annotations

import re
import traceback

import gradio as gr

from mr_maker import DEFAULT_COOKIES_FILE, DEFAULT_MODEL, make_mr


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def clean_error(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


def friendly_error(exc: Exception, details: str) -> str:
    message = clean_error(str(exc))
    lower_details = details.lower()

    if "sign in to confirm" in lower_details or "not a bot" in lower_details:
        return (
            "YouTube에서 자동 다운로드를 막았습니다.\n\n"
            "앱 폴더에 cookies.txt가 있는지 확인한 뒤 다시 시도해 주세요.\n"
            f"필요한 위치: {DEFAULT_COOKIES_FILE}\n\n"
            f"원본 오류: {message}"
        )

    if "requested format is not available" in lower_details:
        return (
            "이 영상에서 내려받을 수 있는 오디오 형식을 찾지 못했습니다.\n\n"
            "다른 영상으로 테스트하거나 cookies.txt를 새로 만든 뒤 다시 시도해 주세요.\n\n"
            f"원본 오류: {message}"
        )

    if "could not copy chrome cookie database" in lower_details or "failed to decrypt with dpapi" in lower_details:
        return (
            "브라우저 쿠키를 직접 읽지 못했습니다.\n\n"
            "이 앱은 화면에서 브라우저를 고르지 않고, 앱 폴더의 cookies.txt를 자동으로 사용합니다.\n"
            f"cookies.txt를 여기에 저장해 주세요: {DEFAULT_COOKIES_FILE}\n\n"
            f"원본 오류: {message}"
        )

    if "couldn't find appropriate backend" in lower_details:
        return (
            "MR 파일 저장에 필요한 오디오 저장 구성요소를 찾지 못했습니다.\n\n"
            "PowerShell에서 다음 명령을 실행한 뒤 다시 시도해 주세요:\n"
            "python -m pip install -U soundfile\n\n"
            f"원본 오류: {message}"
        )

    return f"처리 중 오류가 발생했습니다.\n\n{message}\n\n{details}"


def create_mr(url: str) -> tuple[str, str | None]:
    url = (url or "").strip()
    if not url:
        return "YouTube 링크를 입력해 주세요.", None

    try:
        result = make_mr(url=url, model=DEFAULT_MODEL)
        message = (
            "완료되었습니다.\n\n"
            f"제목: {result.title}\n"
            f"MR 파일: {result.instrumental}"
        )
        return message, str(result.instrumental)
    except Exception as exc:
        details = clean_error(traceback.format_exc())
        return friendly_error(exc, details), None


with gr.Blocks(title="Vocal MR Maker") as demo:
    gr.Markdown("# Vocal MR Maker")
    gr.Markdown("YouTube 링크를 넣으면 보컬을 제거한 MR 파일을 만듭니다.")

    url_input = gr.Textbox(
        label="YouTube 링크",
        placeholder="https://www.youtube.com/watch?v=...",
    )
    run_button = gr.Button("MR 만들기", variant="primary")
    status_output = gr.Textbox(label="상태", lines=8)
    audio_output = gr.Audio(label="완성된 MR", type="filepath")

    run_button.click(
        fn=create_mr,
        inputs=[url_input],
        outputs=[status_output, audio_output],
    )


if __name__ == "__main__":
    demo.queue(max_size=10).launch()
