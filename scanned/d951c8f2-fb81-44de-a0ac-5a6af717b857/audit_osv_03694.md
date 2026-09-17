# [H] ALPINE-CVE-2026-4224

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-4224
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4224
Type: osv

## Affected
- Alpine:v3.24: `python3` — affected >=0 <3.14.5-r0

## Details
When an Expat parser with a registered ElementDeclHandler parses an inline
document type definition containing a deeply nested content model a C stack
overflow occurs.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4224
