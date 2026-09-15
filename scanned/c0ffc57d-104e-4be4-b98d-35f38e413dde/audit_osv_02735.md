# [C] ALPINE-CVE-2022-48174

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-48174
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-48174
Type: osv

## Affected
- Alpine:v3.18: `busybox` — affected >=0 <1.36.1-r1
- Alpine:v3.19: `busybox` — affected >=0 <1.36.1-r2
- Alpine:v3.20: `busybox` — affected >=0 <1.36.1-r2
- Alpine:v3.21: `busybox` — affected >=0 <1.36.1-r2
- Alpine:v3.22: `busybox` — affected >=0 <1.36.1-r2
- Alpine:v3.23: `busybox` — affected >=0 <1.36.1-r2
- Alpine:v3.24: `busybox` — affected >=0 <1.36.1-r2

## Details
There is a stack overflow vulnerability in ash.c:6030 in busybox before 1.35. In the environment of Internet of Vehicles, this vulnerability can be executed from command to arbitrary code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-48174
