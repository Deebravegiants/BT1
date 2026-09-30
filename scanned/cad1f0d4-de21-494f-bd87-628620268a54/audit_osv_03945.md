# [H] ALPINE-CVE-2026-7210

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-7210
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-7210
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
`xml.parsers.expat` and `xml.etree.ElementTree` use insufficient entropy for Expat hash-flooding protection, which allows a crafted XML document to trigger hash flooding.\r\n\r\nFully mitigating this vulnerability requires both updating libexpat to 2.8.0 or later and applying this patch.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-7210
