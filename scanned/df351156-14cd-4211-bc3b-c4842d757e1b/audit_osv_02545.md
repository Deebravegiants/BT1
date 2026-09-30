# [H] ALPINE-CVE-2022-30065

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-30065
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30065
Type: osv

## Affected
- Alpine:v3.13: `busybox` — affected >=0 <1.32.1-r9
- Alpine:v3.14: `busybox` — affected >=0 <1.33.0-r8
- Alpine:v3.15: `busybox` — affected >=0 <1.34.0-r6
- Alpine:v3.16: `busybox` — affected >=0 <1.35.0-r15
- Alpine:v3.17: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.18: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.19: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.20: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.21: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.22: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.23: `busybox` — affected >=0 <1.35.0-r17
- Alpine:v3.24: `busybox` — affected >=0 <1.35.0-r17

## Details
A use-after-free in Busybox 1.35-x's awk applet leads to denial of service and possibly code execution when processing a crafted awk pattern in the copyvar function.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30065
