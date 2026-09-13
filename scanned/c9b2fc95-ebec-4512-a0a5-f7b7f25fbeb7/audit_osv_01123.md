# [H] ALPINE-CVE-2018-20330

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20330
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20330
Type: osv

## Affected
- Alpine:v3.10: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.11: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.12: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.13: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.14: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.15: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.16: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.17: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.18: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.19: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.20: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.21: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.22: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.23: `libjpeg-turbo` — affected >=0 <2.0.2-r0
- Alpine:v3.24: `libjpeg-turbo` — affected >=0 <2.0.2-r0

## Details
The tjLoadImage function in libjpeg-turbo 2.0.1 has an integer overflow with a resultant heap-based buffer overflow via a BMP image because multiplication of pitch and height is mishandled, as demonstrated by tjbench.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20330
