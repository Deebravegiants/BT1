# [M] ALPINE-CVE-2018-19664

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19664
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19664
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
libjpeg-turbo 2.0.1 has a heap-based buffer over-read in the put_pixel_rows function in wrbmp.c, as demonstrated by djpeg.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19664
