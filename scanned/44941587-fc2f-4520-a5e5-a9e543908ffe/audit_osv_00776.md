# [C] ALPINE-CVE-2017-8287

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-8287
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8287
Type: osv

## Affected
- Alpine:v3.10: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.11: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.12: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.13: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.14: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.15: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.16: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.17: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.18: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.19: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.2: `freetype` — affected >=0 <2.5.5-r1
- Alpine:v3.20: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.21: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.22: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.23: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.24: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.3: `freetype` — affected >=0 <2.6.3-r0
- Alpine:v3.4: `freetype` — affected >=0 <2.6.3-r1
- Alpine:v3.5: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.6: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.7: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.8: `freetype` — affected >=0 <2.7.1-r1
- Alpine:v3.9: `freetype` — affected >=0 <2.7.1-r1

## Details
FreeType 2 before 2017-03-26 has an out-of-bounds write caused by a heap-based buffer overflow related to the t1_builder_close_contour function in psaux/psobjs.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8287
