# [M] ALPINE-CVE-2025-14524

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-14524
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-14524
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.33.0 <8.18.0-r0
- Alpine:v3.24: `curl` — affected >=7.33.0 <8.18.0-r0

## Details
When an OAuth2 bearer token is used for an HTTP(S) transfer, and that transfer
performs a cross-protocol redirect to a second URL that uses an IMAP, LDAP,
POP3 or SMTP scheme, curl might wrongly pass on the bearer token to the new
target host.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-14524
