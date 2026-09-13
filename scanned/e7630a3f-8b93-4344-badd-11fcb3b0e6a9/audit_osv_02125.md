# [M] ALPINE-CVE-2021-25292

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-25292
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25292
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.2-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.2-r0

## Details
An issue was discovered in Pillow before 8.1.1. The PDF parser allows a regular expression DoS (ReDoS) attack via a crafted PDF file because of a catastrophic backtracking regex.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25292
