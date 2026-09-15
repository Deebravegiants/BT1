# [H] ALPINE-CVE-2026-45186

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-45186
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-45186
Type: osv

## Affected
- Alpine:v3.20: `expat` — affected >=0 <2.8.1-r0
- Alpine:v3.21: `expat` — affected >=0 <2.8.1-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.1-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.1-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.1-r0

## Details
In libexpat before 2.8.1, the computational complexity of attribute name collision checks allows a denial of service via moderately sized crafted XML input.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-45186
