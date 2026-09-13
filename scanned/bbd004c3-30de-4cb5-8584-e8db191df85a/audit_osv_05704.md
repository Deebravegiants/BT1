# [H] Limit handshake messages we are willing to accept post-handshake in crypto/tls

## Summary
Severity: High
Advisory: BIT-golang-2026-56862
Aliases: CVE-2026-56862, GO-2026-6090
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-golang-2026-56862
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
Handshake messages, such as KeyUpdate, are always considered as state-advancing, regardless of whether a handshake has been completed or not. As a result, a malicious client can keep sending KeyUpdate messages to force the server to keep performing key derivation operations indefinitely.

## References
- https://go.dev/cl/804261
- https://go.dev/issue/80528
- https://groups.google.com/g/golang-announce/c/94pEornpRlI
- https://nvd.nist.gov/vuln/detail/CVE-2026-56862
- https://pkg.go.dev/vuln/GO-2026-6090
