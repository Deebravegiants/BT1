# [M] ALPINE-CVE-2018-6942

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-6942
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6942
Type: osv

## Affected
- Alpine:v3.10: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.11: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.12: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.13: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.14: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.15: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.16: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.17: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.18: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.19: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.20: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.21: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.22: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.23: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.24: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.5: `freetype` — affected >=0 <2.7-r2
- Alpine:v3.6: `freetype` — affected >=0 <2.7.1-r2
- Alpine:v3.7: `freetype` — affected >=0 <2.8.1-r3
- Alpine:v3.8: `freetype` — affected >=0 <2.9-r1
- Alpine:v3.9: `freetype` — affected >=0 <2.9-r1

## Details
An issue was discovered in FreeType 2 through 2.9. A NULL pointer dereference in the Ins_GETVARIATION() function within ttinterp.c could lead to DoS via a crafted font file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6942
