# [H] ALPINE-CVE-2021-42379

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-42379
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-42379
Type: osv

## Affected
- Alpine:v3.11: `busybox` — affected >=1.18.0 <1.31.1-r11
- Alpine:v3.12: `busybox` — affected >=1.18.0 <1.31.1-r21
- Alpine:v3.13: `busybox` — affected >=1.18.0 <1.32.1-r7
- Alpine:v3.14: `busybox` — affected >=1.18.0 <1.33.1-r6
- Alpine:v3.15: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.16: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.17: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.18: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.19: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.20: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.21: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.22: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.23: `busybox` — affected >=1.18.0 <1.34.0-r0
- Alpine:v3.24: `busybox` — affected >=1.18.0 <1.34.0-r0

## Details
A use-after-free in Busybox's awk applet leads to denial of service and possibly code execution when processing a crafted awk pattern in the next_input_file function

## References
- https://security.alpinelinux.org/vuln/CVE-2021-42379
