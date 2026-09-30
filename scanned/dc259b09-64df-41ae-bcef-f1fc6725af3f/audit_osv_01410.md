# [H] ALPINE-CVE-2019-13304

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13304
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13304
Type: osv

## Affected
- Alpine:v3.10: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.8: `imagemagick` — affected >=0 <6.9.10.53-r0
- Alpine:v3.9: `imagemagick` — affected >=0 <6.9.10.53-r0

## Details
ImageMagick 7.0.8-50 Q16 has a stack-based buffer overflow at coders/pnm.c in WritePNMImage because of a misplaced assignment.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13304
