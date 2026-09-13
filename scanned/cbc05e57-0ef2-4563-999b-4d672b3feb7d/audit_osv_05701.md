# [H] Apply ReadHeaderTimeout when doing unencrypted HTTP/2 check in net/http

## Summary
Severity: High
Advisory: BIT-golang-2026-56853
Aliases: CVE-2026-56853, GO-2026-6089
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-golang-2026-56853
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
When a server is configured to support unencrypted HTTP/2, it reads a few bytes from each new connection to see if they contain the HTTP/2 client preface. ReadHeaderTimeout is unexpectedly not being applied when doing this.

## References
- https://go.dev/cl/795540
- https://go.dev/issue/80205
- https://groups.google.com/g/golang-announce/c/94pEornpRlI
- https://nvd.nist.gov/vuln/detail/CVE-2026-56853
- https://pkg.go.dev/vuln/GO-2026-6089
