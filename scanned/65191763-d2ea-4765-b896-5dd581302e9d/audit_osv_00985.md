# [H] ALPINE-CVE-2018-14550

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14550
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14550
Type: osv

## Affected
- Alpine:v3.10: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.11: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.12: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.13: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.14: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.15: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.16: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.17: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.18: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.19: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.20: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.21: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.22: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.23: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.24: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.6: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.7: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.8: `libpng` — affected >=0 <1.6.37-r0
- Alpine:v3.9: `libpng` — affected >=0 <1.6.37-r0

## Details
An issue has been found in third-party PNM decoding associated with libpng 1.6.35. It is a stack-based buffer overflow in the function get_token in pnm2png.c in pnm2png.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14550
