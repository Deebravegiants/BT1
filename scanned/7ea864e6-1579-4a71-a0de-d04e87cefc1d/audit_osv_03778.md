# [M] ALPINE-CVE-2026-4873

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-4873
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4873
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.20.0 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.20.0 <8.20.0-r0

## Details
A vulnerability exists where a connection requiring TLS incorrectly reuses an
existing unencrypted connection from the same connection pool. If an initial
transfer is made in clear-text (via IMAP, SMTP, or POP3), a subsequent request
to that same host bypasses the TLS requirement and instead transmit data
unencrypted.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4873
