# [H] nebula-mesh: Web UI and API responses lack security headers (CSP, X-Frame-Options, HSTS, etc.)

## Summary
Severity: High
Advisory: GHSA-w7w5-5gcp-38rw
CVE: CVE-2026-47723
CWE: CWE-1021
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-w7w5-5gcp-38rw
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.1

## Details
None of the response paths in `internal/web/` or `internal/api/` set the standard browser-security headers. `grep` for `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy` returns zero matches across the codebase.

## Impact
The admin UI signs CA certificates, mints API keys (returned inline once per page), displays TOTP QR codes, and exposes operator-management forms. Missing `X-Frame-Options: DENY` / `frame-ancestors 'none'` is a real clickjacking lever against an admin browsing `/ui/operators/*` or `/ui/cas/*`. Missing `X-Content-Type-Options: nosniff` allows MIME confusion on any user-supplied content surface. Missing HSTS on TLS deployments leaves a downgrade window.

## Affected
All released versions up to v0.3.0.

## Suggested fix
A single response-header middleware mounted at the chi router root in both `/ui/*` and `/api/*` paths:

```go
func securityHeadersMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(rw http.ResponseWriter, r *http.Request) {
        h := rw.Header()
        h.Set("Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        h.Set("X-Content-Type-Options", "nosniff")
        h.Set("Referrer-Policy", "same-origin")
        h.Set("X-Frame-Options", "DENY")  // belt-and-braces; CSP frame-ancestors is the modern path
        if r.TLS != nil {
            h.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        }
        next.ServeHTTP(rw, r)
    })
}
```

The inline `<script>` in `layout.html` for CSRF wiring (added in the CSRF advisory) will need either a nonce, a hash in CSP, or external-file extraction. Easiest path: a nonce per request (`crypto/rand`, base64) injected into both the CSP header and the script's `nonce=""` attribute.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-w7w5-5gcp-38rw
- https://github.com/forgekeep/nebula-mesh/commit/b45fda5476c41ffcff1ca23058aef0fb851359c1
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.3.1
- https://github.com/juev/nebula-mesh
