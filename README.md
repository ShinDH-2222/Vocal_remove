# Vocal MR Maker

YouTube URL에서 오디오를 내려받고 Demucs로 보컬을 제거해 MR/instrumental 파일을 만드는 Python 앱입니다.

## 준비

FFmpeg가 설치되어 있어야 합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 웹 앱 실행

```powershell
python app.py
```

브라우저에서 표시되는 로컬 주소를 열고 YouTube 링크를 입력하면 됩니다.

## CLI 실행

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 참고

YouTube 영상과 음원의 저작권, 플랫폼 이용약관을 지켜서 개인적으로 사용 가능한 콘텐츠에만 사용하세요.
