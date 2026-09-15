# [H] ALPINE-CVE-2018-1000500

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000500
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000500
Type: osv

## Affected
- Alpine:v3.10: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.11: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.12: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.13: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.14: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.15: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.16: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.17: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.18: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.19: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.20: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.21: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.22: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.23: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.24: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.8: `busybox` — affected >=0 <1.28.3-r2
- Alpine:v3.9: `busybox` — affected >=0 <1.28.3-r2

## Details
Busybox contains a Missing SSL certificate validation vulnerability in The "busybox wget" applet that can result in arbitrary code execution. This attack appear to be exploitable via Simply download any file over HTTPS using "busybox wget https://compromised-domain.com/important-file".

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000500
