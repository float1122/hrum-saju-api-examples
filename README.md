# hrum-saju-api-examples

생년월일시로 사주 만세력(원국 네 기둥의 천간·지지, 오행, 용신, 대운)을 받아 오는 최소 예제예요. HRUM(흐름) 만세력 API(`POST /manseryeok`)를 Node와 Python으로 한 번씩 불러요.

- 시작 가이드: https://hrum.ai/getting-started.html
- 만세력 API: https://hrum.ai/manseryeok-api.html
- 전체 레퍼런스: https://hrum.ai/docs.html

## 준비

1. https://console.hrum.ai 에서 가입하고 「API 키」 화면에서 키를 발급해요. 키는 발급 직후 한 번만 보여요.
2. `.env.example`을 `.env`로 복사하고 `HRUM_API_KEY=` 뒤에 키를 넣어요.

```bash
cp .env.example .env
```

키는 서버에서만 쓰세요. 브라우저·모바일 앱 코드에 넣지 마세요. `.env`는 `.gitignore`에 들어 있어요.

키 없이 결과부터 보고 싶으면 플레이그라운드(https://hrum.ai/playground.html)를 써 보세요.

## Node (18 이상)

의존성 없음. 기본 `fetch`를 써요.

```bash
node examples/node/index.mjs
node examples/node/index.mjs --date 1990-05-15 --time 12:00 --gender male
node examples/node/index.mjs --date 1990-07-15 --lunar --gender female
```

## Python (3.8 이상)

```bash
pip install requests
python examples/python/main.py
python examples/python/main.py --date 1990-05-15 --time 12:00 --gender male
python examples/python/main.py --date 1990-07-15 --lunar --gender female
```

표준 라이브러리 `urllib`는 기본 User-Agent가 보안 규칙에 걸려 403이 와요. `requests`를 쓰거나 `User-Agent` 헤더를 직접 넣으세요.

## 옵션

| 옵션 | 뜻 |
|---|---|
| `--date YYYY-MM-DD` | 생년월일 |
| `--time HH:MM` | 출생 시각. `--date`만 주고 이 값을 빼면 "시간 미상"으로 보내요 |
| `--gender male\|female` | 성별 (필수 필드) |
| `--lunar` | 음력 생일로 보냄 (`calendar: "lunar"`) |
| `--leap` | 윤달 (`isLeapMonth: true`) |

예제는 `timezone: "Asia/Seoul"`로 고정해 보내요. 해외 출생이면 코드에서 바꾸세요.

## 알아 두면 좋은 것

- **인증**: `X-Partner-Api-Key` 헤더. 기본 주소 `https://api.hrum.ai/api/v1/partners/v1`
- **응답**: 성공 `{"success": true, "data": {...}}`, 실패 `{"success": false, "statusCode": ..., "message": ..., "timestamp": ...}`. `code`는 일부 오류(예: `INVALID_LOCATION`)에만 붙어요. 분기는 `statusCode`로, `code`는 있을 때만
- **천간·지지**: `data.wonkuk.year|month|day|hour`의 `stem`·`branch`(한글)와 `stemHanja`·`branchHanja`(한자). 일주의 천간이 일간
- **시간 미상**: `hour`·`minute`를 빼고 보내면 `wonkuk.hour`가 `null`, `birthHour.known === false` (시간을 보내면 `birthHour`는 `null`). 정오 같은 값을 넣어 보내지 마세요
- **음력**: 없는 윤달·없는 날짜는 400 (`code` 없음). 변환 결과는 `lunarInput.solarDate`
- **타임존**: `timezone`은 필수. 인식 못 하는 이름이면 성공 응답의 `data.warnings`에 `{ "code": "UNKNOWN_TIMEZONE", "field": "timezone" }`이 붙어요
- **진태양시·자시**: `birthLatitude`·`birthLongitude`(또는 `country`), `zaSiRule`, `birthTimePrecision` 옵션은 레퍼런스 참고
- **저장해서 다시 쓰기**: 같은 입력이면 결과가 같아요. 성공한 요청은 매번 과금되니 첫 응답을 저장해 두고 다시 쓰세요

## 라이선스

MIT — FLOAT Co., Ltd.
