# [H] ALPINE-CVE-2026-80255

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-80255
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-80255
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
A `Set-Cookie:` header using tab (horizontal tab, ASCII code 9) instead of
space (ascii code 32) immediately before the `Secure` attribute causes curl to
store the cookie without its Secure flag. The cookie might then wrongfully be
sent over plaintext HTTP on subsequent requests to the same host.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-80255
