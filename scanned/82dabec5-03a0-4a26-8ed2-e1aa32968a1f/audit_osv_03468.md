# [H] ALPINE-CVE-2026-15308

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-15308
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-15308
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
The incremental HTML parser (html.parser.HTMLParser) allows for CPU
denial-of-service through repeated unterminated markup declarations when
processing uncontrolled data.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-15308
