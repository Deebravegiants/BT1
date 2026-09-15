# [M] ALPINE-CVE-2021-42374

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-42374
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-42374
Type: osv

## Affected
- Alpine:v3.11: `busybox` — affected >=1.27.0 <1.31.1-r11
- Alpine:v3.12: `busybox` — affected >=1.27.0 <1.31.1-r21
- Alpine:v3.13: `busybox` — affected >=1.27.0 <1.32.1-r7
- Alpine:v3.14: `busybox` — affected >=1.27.0 <1.33.1-r4
- Alpine:v3.15: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.16: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.17: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.18: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.19: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.20: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.21: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.22: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.23: `busybox` — affected >=1.27.0 <1.34.0-r0
- Alpine:v3.24: `busybox` — affected >=1.27.0 <1.34.0-r0

## Details
An out-of-bounds heap read in Busybox's unlzma applet leads to information leak and denial of service when crafted LZMA-compressed input is decompressed. This can be triggered by any applet/format that

## References
- https://security.alpinelinux.org/vuln/CVE-2021-42374
