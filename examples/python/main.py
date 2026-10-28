"""HRUM manseryeok example (Python 3.8+, server-side only).

Usage:
    python examples/python/main.py
    python examples/python/main.py --date 1990-05-15 --time 12:00 --gender male
    python examples/python/main.py --date 1990-07-15 --lunar --gender female   # no --time = hour unknown
"""
import argparse
import json
import os
import sys

DEFAULT_BASE = "https://api.hrum.ai/api/v1/partners/v1"


def load_dotenv(path):
    """Minimal .env loader (KEY=VALUE lines). Real environment variables win."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def build_body(args):
    year, month, day = (int(x) for x in args.date.split("-"))
    body = {"year": year, "month": month, "day": day, "timezone": "Asia/Seoul", "gender": args.gender}
    # Omit hour/minute entirely when unknown. Do not send a guessed noon.
    if args.time:
        hour, _, minute = args.time.partition(":")
        body["hour"] = int(hour)
        body["minute"] = int(minute or 0)
    if args.lunar:
        body["calendar"] = "lunar"
        body["isLeapMonth"] = args.leap
    return body


def pillar_label(p):
    if not p:
        return "미상"
    return f'{p["stemHanja"]}{p["branchHanja"]} ({p["stem"]}{p["branch"]}, {p["ohaeng"]})'


def main():
    parser = argparse.ArgumentParser(description="HRUM manseryeok example")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--time", default=None, help="HH:MM (omit if unknown)")
    parser.add_argument("--gender", default="male", choices=["male", "female"])
    parser.add_argument("--lunar", action="store_true")
    parser.add_argument("--leap", action="store_true")
    args = parser.parse_args()
    if args.date is None:
        args.date, args.time = "1990-05-15", args.time or "12:00"

    load_dotenv(os.path.join(os.getcwd(), ".env"))
    api_key = os.environ.get("HRUM_API_KEY", "")
    base = os.environ.get("HRUM_API_BASE") or DEFAULT_BASE

    if not api_key:
        print(
            "HRUM_API_KEY가 없어요. .env.example을 .env로 복사하고 "
            "콘솔(https://console.hrum.ai)에서 발급한 키를 넣어 주세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import requests  # urllib's default User-Agent gets a 403; use requests
    except ImportError:
        print("requests가 필요해요: pip install requests", file=sys.stderr)
        sys.exit(1)

    body = build_body(args)
    try:
        res = requests.post(
            f"{base}/manseryeok",
            headers={"X-Partner-Api-Key": api_key},
            json=body,
            timeout=30,
        )
        data = res.json()
    except requests.RequestException as err:
        print(f"호출 중 오류: {err}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print(f"응답을 JSON으로 읽지 못했어요 (HTTP {res.status_code}).", file=sys.stderr)
        sys.exit(1)

    if not data.get("success"):
        # Branch on statusCode/code only. message text may change.
        print(f'요청 실패: {data.get("statusCode", res.status_code)} {data.get("code") or ""}'.strip(), file=sys.stderr)
        if data.get("statusCode") == 401:
            print("API 키와 헤더 이름(X-Partner-Api-Key)을 확인해 주세요.", file=sys.stderr)
        if data.get("statusCode") == 402:
            print("크레딧이 부족해요. 콘솔에서 잔액을 확인해 주세요.", file=sys.stderr)
        if data.get("code") == "INVALID_LUNAR_DATE":
            print("그해에 없는 음력 날짜나 윤달일 수 있어요. 입력을 다시 확인해 주세요.", file=sys.stderr)
        # message is for humans/logs only (may be a string or a list).
        msg = data.get("message")
        if data.get("statusCode") == 400 and msg:
            print("상세:", " / ".join(msg if isinstance(msg, list) else [str(msg)]), file=sys.stderr)
        sys.exit(1)

    d = data["data"]
    w = d["wonkuk"]
    print("요청:", json.dumps(body, ensure_ascii=False))
    print("년주", pillar_label(w.get("year")))
    print("월주", pillar_label(w.get("month")))
    print("일주", pillar_label(w.get("day")), "<- 일간 =", w["day"]["stem"])
    print("시주", pillar_label(w.get("hour")))
    if (d.get("birthHour") or {}).get("known") is False:
        print("출생 시각 미상: 분석 값은 년·월·일 세 기둥 기준이에요.")
    if d.get("lunarInput"):
        print("음력 → 양력:", d["lunarInput"].get("solarDate"))
    print("오행 분포", json.dumps(d.get("ohaengBalance"), ensure_ascii=False))
    print("용신", d.get("yongshin"), "/ 대운", d.get("daeunDirection"), d.get("daeunNumber"))
    if d.get("warnings"):
        print("경고", json.dumps(d["warnings"], ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    main()
