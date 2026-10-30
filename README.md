# THM Korea

thm.rubiworkshop.com 원페이지 정적 사이트. quoc.rubiworkshop.com과 같은 구조와 디자인(레이아웃, 서체, 빌드 방식)입니다.

- `index.html` 한국어 원페이지 (THM · RANGE · CLAVICULA · FIBULA · COCKPIT · MANDIBULA · FIT · STORY · SHOWROOM)
- 디자인은 QUOC 사이트와 같은 rubi.kr 체계: 영문 Pretendard · 한글 에스코어 드림, 웨이트 400, 흑백과 얇은 라인, 각진 버튼, 라이트/다크 자동. 일본어 페이지는 빌드 시 Noto Sans JP로 바뀝니다.
- QUOC와 다른 점: THM 공식 제품 사진(1300 x 1040, 5:4 블랙 스튜디오 컷)에 맞춰 사진 비율을 5:4로 맞췄고, 라벨과 아이브로우는 대문자 변환 없이 원문 대소문자로 표기합니다. 사이즈 표 대신 크랭크·핸들바 호환 표(Fit Guide)가 들어갑니다.
- `en/index.html`, `ja/index.html` 영어 · 일본어 페이지 (빌드로 생성, 직접 수정하지 않음)
- `index.src.html` 편집용 한국어 원본. 호환 표는 `{{CRANK_TABLE}}`, `{{BAR_TABLE}}` 자리에 빌드 시 채워집니다 (`tools/build.py` 안의 수치).
- `i18n/` 번역 사전 (`ko.json` 원문 목록, `en.json` · `ja.json` 원문→번역, `tr_source.py` 번역 원본)
- `tools/build.py` 한국어 페이지, 번역 페이지, sitemap.xml을 한 번에 생성
- `404.html` 하위 주소(/clavicula, /dm, /xc, /fibula, /tibia, /frontale, /mandibula, /fit, /dealers 등)를 섹션으로 연결
- `images/` 섹션별 이미지 (`hero`, `brand`, `clavicula`, `clavicula-dm`, `clavicula-xc`, `fibula`, `tibia`, `ulna`, `frontale`, `frontale-aero`, `mandibula`)
- `.github/image-manifest.txt` + `fetch-images.yml` THM 공식 사이트(thm.bike) 이미지 이전용 워크플로

## 처음 올릴 때
1. 저장소 `sereno-kwon/thm`을 만들고 이 폴더를 main에 푸시합니다.
2. 푸시하면 `fetch-images.yml`이 매니페스트의 이미지 62장을 thm.bike에서 받아 `images/`에 커밋합니다. Actions → Fetch images from THM에서 FAIL이 있으면 해당 줄의 URL을 바꿔 다시 푸시합니다.
3. 배포: GitHub Pages(Settings → Pages → main / root) 또는 Cloudflare Pages(저장소 연결, 빌드 명령 없음, 출력 폴더 `/`) 중 하나를 씁니다.
4. 도메인 DNS에 `thm` CNAME 레코드를 추가합니다 (GitHub Pages는 `sereno-kwon.github.io`, Cloudflare Pages는 `<프로젝트>.pages.dev`). CNAME 파일은 이미 들어 있습니다.
5. 파비콘은 별도로 넣어야 합니다: `images/favicon-48.png`, `images/favicon-96.png`, `images/apple-touch-icon.png`(180px), `images/logo-512.png`.
6. 로고(`images/logo-white.png`)는 thm.bike 헤더 로고(200 x 40)를 받아 옵니다. CSS에서 헤더는 검정, 다크모드는 흰색으로 칠해지며, 더 선명한 로고 원본(SVG 또는 큰 PNG)이 있으면 같은 경로에 덮어쓰면 됩니다.

## 이미지
매니페스트를 수정해 main에 푸시하면 Actions가 이미지를 받아 `images/`에 커밋합니다.
이미 받은 파일은 건너뛰므로, 이미지를 교체할 때는 해당 파일을 지우거나 새 파일명으로 추가합니다.
루비에서 직접 촬영한 사진으로 바꿀 때는 같은 경로에 덮어쓰면 됩니다. 히어로 02, 03과 brand 04, 05는 PNG입니다.

## 문구 수정과 번역
1. `index.src.html`의 한국어 문구를 고칩니다.
2. `python3 tools/build.py` 로 한국어 페이지를 만들고, `python3 i18n/extract.py` 로 `ko.json`을 갱신합니다.
3. 새로 생기거나 바뀐 한국어 문장을 `en.json` · `ja.json`에 같은 키로 추가합니다 (또는 `i18n/tr_source.py`의 목록을 같은 순서로 고친 뒤 `python3 i18n/tr_source.py`). HTML 태그는 원문과 똑같이 유지합니다.
4. 다시 `python3 tools/build.py` 를 실행하면 번역되지 않은 문장이 있을 때 목록으로 알려줍니다.

빌드에는 `beautifulsoup4`가 필요합니다 (`pip install beautifulsoup4`).

## 링크
- 헤더 SHOP, 각 제품의 "루비워크샵에서 보기" 버튼: `https://rubiworkshop.com/thm`
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat`
- 푸터 INSTAGRAM: `https://www.instagram.com/rubi.workshop` (THM 코리아 계정이 생기면 교체)
- 쇼룸 운영시간: 월~금 12:00~19:00, 토 10:00~15:30

## 한글 표기
클라비큘라(Clavicula), 피뷸라(Fibula), 티비아(Tibia), 울나(Ulna), 프론탈레(Frontale), 만디불라(Mandibula), 스카풀라(Scapula), 알트 두벤슈테트(Alt Duvenstedt), 토마스 메르틴(Thomas Mertin), 쉬몰케 카본(Schmolke Carbon), 카본티(Carbon-Ti)

## 수치 출처
THM 공식 사이트 thm.bike 제품별 Technical Info (2026-10 확인). 무게는 ±5%.
