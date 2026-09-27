# [C] ALPINE-CVE-2018-14600

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-14600
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14600
Type: osv

## Affected
- Alpine:v3.10: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.11: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.12: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.13: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.14: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.15: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.16: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.17: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.18: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.19: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.20: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.21: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.22: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.23: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.24: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.5: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.6: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.7: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.8: `libx11` — affected >=0 <1.6.6-r0
- Alpine:v3.9: `libx11` — affected >=0 <1.6.6-r0

## Details
An issue was discovered in libX11 through 1.6.5. The function XListExtensions in ListExt.c interprets a variable as signed instead of unsigned, resulting in an out-of-bounds write (of up to 128 bytes), leading to DoS or remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14600
