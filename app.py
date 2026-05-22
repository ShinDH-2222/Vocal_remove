from __future__ import annotations

import traceback

import gradio as gr

from mr_maker import make_mr


def create_mr(url: str, model: str) -> tuple[str, str | None]:
    url = url.strip()
    if not url:
        return "YouTube 링크를 입력해 주세요.", None

    try:
        result = make_mr(url, model=model)
        message = (
            f"완료: {result.title}\n"
            f"원본 오디오: {result.source_audio}\n"
            f"MR 파일: {result.instrumental}"
        )
        return message, str(result.instrumental)
    except Exception as exc:
        details = traceback.format_exc()
        return f"실패: {exc}\n\n{details}", None


with gr.Blocks(title="Vocal MR Maker") as demo:
    gr.Markdown("# Vocal MR Maker")
    gr.Markdown("YouTube 링크를 입력하면 오디오를 추출하고 보컬을 제거해 MR 파일을 만듭니다.")

    with gr.Row():
        url_input = gr.Textbox(label="YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        model_input = gr.Dropdown(
            label="Demucs 모델",
            choices=["htdemucs", "htdemucs_ft", "mdx_extra"],
            value="htdemucs",
        )

    run_button = gr.Button("MR 만들기", variant="primary")
    status_output = gr.Textbox(label="상태", lines=8)
    audio_output = gr.Audio(label="MR 미리듣기/다운로드", type="filepath")

    run_button.click(
        fn=create_mr,
        inputs=[url_input, model_input],
        outputs=[status_output, audio_output],
    )


if __name__ == "__main__":
    demo.launch()
