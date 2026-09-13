# [H] ALPINE-CVE-2020-13790

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-13790
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-13790
Type: osv

## Affected
- Alpine:v3.10: `libjpeg-turbo` — affected >=0 <2.0.4-r1
- Alpine:v3.11: `libjpeg-turbo` — affected >=0 <2.0.4-r1
- Alpine:v3.12: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.13: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.14: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.15: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.16: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.17: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.18: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.19: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.20: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.21: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.22: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.23: `libjpeg-turbo` — affected >=0 <2.0.4-r2
- Alpine:v3.24: `libjpeg-turbo` — affected >=0 <2.0.4-r2

## Details
libjpeg-turbo 2.0.4, and mozjpeg 4.0.0, has a heap-based buffer over-read in get_rgb_row() in rdppm.c via a malformed PPM input file.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-13790
