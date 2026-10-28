// HRUM manseryeok example (Node 18+, server-side only).
// Usage:
//   node examples/node/index.mjs
//   node examples/node/index.mjs --date 1990-05-15 --time 12:00 --gender male
//   node examples/node/index.mjs --date 1990-07-15 --lunar --gender female   (no --time = hour unknown)
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const DEFAULT_BASE = 'https://api.hrum.ai/api/v1/partners/v1';

// Minimal .env loader (KEY=VALUE lines). Real environment variables win.
function loadDotEnv(path) {
  if (!existsSync(path)) return;
  for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$/);
    if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2];
  }
}

function parseArgs(argv) {
  const args = { date: '1990-05-15', time: '12:00', gender: 'male', lunar: false, leap: false };
  let timeGiven = false;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--date') args.date = argv[++i];
    else if (a === '--time') { args.time = argv[++i]; timeGiven = true; }
    else if (a === '--gender') args.gender = argv[++i];
    else if (a === '--lunar') args.lunar = true;
    else if (a === '--leap') args.leap = true;
  }
  // If a date was passed without --time, treat birth hour as unknown.
  if (argv.includes('--date') && !timeGiven) args.time = null;
  return args;
}

function buildBody({ date, time, gender, lunar, leap }) {
  const [year, month, day] = date.split('-').map(Number);
  const body = { year, month, day, timezone: 'Asia/Seoul', gender };
  if (time) {
    const [hour, minute] = time.split(':').map(Number);
    body.hour = hour;
    body.minute = minute ?? 0;
  }
  // Omit hour/minute entirely when unknown. Do not send a guessed noon.
  if (lunar) {
    body.calendar = 'lunar';
    body.isLeapMonth = leap;
  }
  return body;
}

function pillarLabel(p) {
  return p ? `${p.stemHanja}${p.branchHanja} (${p.stem}${p.branch}, ${p.ohaeng})` : '미상';
}

async function main() {
  loadDotEnv(resolve(process.cwd(), '.env'));
  const apiKey = process.env.HRUM_API_KEY;
  const base = process.env.HRUM_API_BASE || DEFAULT_BASE;

  if (!apiKey) {
    console.error('HRUM_API_KEY가 없어요. .env.example을 .env로 복사하고 콘솔(https://console.hrum.ai)에서 발급한 키를 넣어 주세요.');
    process.exit(1);
  }

  const body = buildBody(parseArgs(process.argv.slice(2)));
  const res = await fetch(`${base}/manseryeok`, {
    method: 'POST',
    headers: { 'X-Partner-Api-Key': apiKey, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  let json;
  try {
    json = await res.json();
  } catch {
    console.error(`응답을 JSON으로 읽지 못했어요 (HTTP ${res.status}).`);
    process.exit(1);
  }

  if (!json.success) {
    // Branch on statusCode/code only. message text may change.
    console.error(`요청 실패: ${json.statusCode ?? res.status} ${json.code ?? ''}`.trim());
    if (json.statusCode === 401) console.error('API 키와 헤더 이름(X-Partner-Api-Key)을 확인해 주세요.');
    if (json.statusCode === 402) console.error('크레딧이 부족해요. 콘솔에서 잔액을 확인해 주세요.');
    // A lunar date that does not exist is a plain 400 (no code).
    if (json.statusCode === 400 && body.calendar === 'lunar') console.error('그해에 없는 음력 날짜나 윤달일 수 있어요. 입력을 다시 확인해 주세요.');
    // message is for humans/logs only (may be a string or an array).
    if (json.statusCode === 400 && json.message) console.error('상세:', [].concat(json.message).join(' / '));
    process.exit(1);
  }

  const d = json.data;
  const w = d.wonkuk;
  console.log('요청:', JSON.stringify(body));
  console.log('년주', pillarLabel(w.year));
  console.log('월주', pillarLabel(w.month));
  console.log('일주', pillarLabel(w.day), '<- 일간 =', w.day.stem);
  console.log('시주', pillarLabel(w.hour));
  if (d.birthHour && d.birthHour.known === false) console.log('출생 시각 미상: 분석 값은 년·월·일 세 기둥 기준이에요.');
  if (d.lunarInput) console.log('음력 → 양력:', d.lunarInput.solarDate);
  console.log('오행 분포', d.ohaengBalance);
  console.log('용신', d.yongshin, '/ 대운', d.daeunDirection, d.daeunNumber);
  if (d.warnings?.length) console.warn('경고', d.warnings);
}

main().catch((err) => {
  console.error('호출 중 오류:', err.message);
  process.exit(1);
});
