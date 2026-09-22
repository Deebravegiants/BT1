# [H] ALPINE-CVE-2022-28391

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-28391
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-28391
Type: osv

## Affected
- Alpine:v3.12: `busybox` — affected >=0 <1.31.1-r22
- Alpine:v3.13: `busybox` — affected >=0 <1.32.1-r8
- Alpine:v3.14: `busybox` — affected >=0 <1.33.1-r7
- Alpine:v3.15: `busybox` — affected >=0 <1.34.1-r5
- Alpine:v3.16: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.17: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.18: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.19: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.20: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.21: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.22: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.23: `busybox` — affected >=0 <1.35.0-r7
- Alpine:v3.24: `busybox` — affected >=0 <1.35.0-r7

## Details
BusyBox through 1.35.0 allows remote attackers to execute arbitrary code if netstat is used to print a DNS PTR record's value to a VT compatible terminal. Alternatively, the attacker could choose to change the terminal's colors.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-28391
