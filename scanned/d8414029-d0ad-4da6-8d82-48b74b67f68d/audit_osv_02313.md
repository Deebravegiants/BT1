# [M] ALPINE-CVE-2021-42375

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-42375
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-42375
Type: osv

## Affected
- Alpine:v3.13: `busybox` — affected >=0 <1.32.1-r7
- Alpine:v3.14: `busybox` — affected >=0 <1.33.1-r5
- Alpine:v3.15: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.16: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.17: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.18: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.19: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.20: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.21: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.22: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.23: `busybox` — affected >=0 <1.34.0-r0
- Alpine:v3.24: `busybox` — affected >=0 <1.34.0-r0

## Details
An incorrect handling of a special element in Busybox's ash applet leads to denial of service when processing a crafted shell command, due to the shell mistaking specific characters for reserved characters. This may be used for DoS under rare conditions of filtered command input.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-42375
