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
YouTube에서 봇 확인 오류가 나면 앱의 `Use cookies from local browser`에서 현재 YouTube에 로그인된 브라우저를 선택하세요.
그래도 실패하면 브라우저 쿠키를 `cookies.txt`로 내보낸 뒤 앱의 `Optional YouTube cookies.txt`에 업로드하세요.

Chrome 쿠키 오류가 날 때:

1. Chrome 창을 모두 닫습니다.
2. 작업 관리자에서 남아 있는 `chrome.exe`가 있으면 종료합니다.
3. 다시 실행합니다.
4. 그래도 실패하면 Edge/Firefox로 YouTube에 로그인한 뒤 해당 브라우저를 선택하거나, `cookies.txt`를 직접 업로드합니다.

`Failed to decrypt with DPAPI` 오류가 날 때:

1. Chrome/Edge 대신 Firefox에서 YouTube에 로그인한 뒤 앱에서 `firefox`를 선택합니다.
2. 또는 YouTube 쿠키를 Netscape 형식의 `cookies.txt`로 내보내고 앱에 업로드합니다.
3. 앱은 브라우저 프로필을 가진 동일한 Windows 사용자 세션에서 실행해야 합니다.

`Requested format is not available` 오류가 날 때:

1. Firefox 쿠키 또는 `cookies.txt`로 다시 시도합니다.
2. 특정 영상에서만 실패하면 영상 자체가 사용 가능한 포맷을 제한했을 수 있으므로 다른 영상으로 테스트합니다.
3. 앱은 가능한 오디오/비디오 포맷을 MP3로 변환하도록 fallback을 사용합니다.

공개 서비스로 운영할 때는 YouTube URL 대신 사용자가 직접 권리를 가진 오디오 파일을 업로드하게 하는 방식이 더 안정적입니다.

## CLI 실행

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

이 명령은 YouTube 오디오를 MP3로 추출한 뒤 Demucs로 보컬을 제거합니다.

쿠키 파일을 사용할 때:

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies cookies.txt
```

현재 로그인된 브라우저 쿠키를 바로 사용할 때:

```powershell
python mr_maker.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies-from-browser edge
```

로컬 오디오 파일을 사용할 때:

```powershell
python mr_maker.py --input ".\song.wav"
```

## 참고

YouTube 영상과 음원의 저작권, 플랫폼 이용약관을 지켜서 개인적으로 사용 가능한 콘텐츠에만 사용하세요.
