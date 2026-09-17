# PWA Push

관리자가 메시지를 보내면 푸시를 구독한 브라우저에 알림이 도착하는 아주 작은 PWA Push 예제입니다.

## 기능

- 앱 설치용 manifest 제공
- 홈 화면 추가 또는 설치 프롬프트 대응
- 설치 아이콘 제공
- 서비스워커 등록
- 브라우저 푸시 구독
- 구독 정보 서버 저장
- 관리자 페이지에서 메시지 발송
- 브라우저 알림 표시

## 폴더 구조

```text
pwa-push/
  app/
    main.py
    push_store.py
    templates/
      index.html
      admin.html
    static/
      app.css
      app.js
      admin.js
      sw.js
      manifest.webmanifest
      icon-192.svg
      icon-512.svg
      icon-maskable.svg
  scripts/
    generate_vapid_keys.py
  requirements.txt
```

## 1. VAPID 키 만들기

먼저 아래 명령으로 키를 생성합니다.

```bash
cd C:\workspace\workspace_python\pwa-push
python scripts\generate_vapid_keys.py
```

## 2. 환경변수 설정

cmd 예시:

```cmd
set PWA_VAPID_PUBLIC_KEY=여기에_생성된_public_key
set PWA_VAPID_PRIVATE_KEY=여기에_생성된_private_key
set PWA_VAPID_SUBJECT=mailto:admin@example.com
```

영구 저장이 필요하면 `setx`를 사용할 수 있습니다.

```cmd
setx PWA_VAPID_PUBLIC_KEY "여기에_생성된_public_key"
setx PWA_VAPID_PRIVATE_KEY "여기에_생성된_private_key"
setx PWA_VAPID_SUBJECT "mailto:admin@example.com"
```

`setx`는 새로 연 `cmd` 창부터 적용됩니다.

## 3. 서버 실행

```bash
pip install pywebpush
python -m uvicorn app.main:app --reload --port 8020
```

## 4. 사용 방법

1. `/` 페이지 접속
2. 가능하면 `앱처럼 설치` 또는 브라우저의 `홈 화면에 추가`
3. 서비스워커 등록
4. 푸시 구독 버튼 클릭
5. `/admin` 페이지에서 제목/내용 입력
6. 푸시 보내기 버튼 클릭
7. 구독한 브라우저에서 알림 확인

## 모바일 테스트 팁

- 모바일에서는 HTTPS 주소가 사실상 필요합니다.
- `ngrok` 같은 HTTPS 터널을 사용하면 테스트가 편합니다.
- Android는 설치 프롬프트가 보일 수 있고, iPhone은 Safari에서 `홈 화면에 추가`로 설치하는 흐름이 일반적입니다.
