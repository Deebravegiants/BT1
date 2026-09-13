# [H] ALPINE-CVE-2019-17069

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-17069
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17069
Type: osv

## Affected
- Alpine:v3.10: `putty` — affected >=0 <0.73-r0
- Alpine:v3.11: `putty` — affected >=0 <0.73-r0
- Alpine:v3.12: `putty` — affected >=0 <0.73-r0
- Alpine:v3.13: `putty` — affected >=0 <0.73-r0
- Alpine:v3.14: `putty` — affected >=0 <0.73-r0
- Alpine:v3.15: `putty` — affected >=0 <0.73-r0
- Alpine:v3.16: `putty` — affected >=0 <0.73-r0
- Alpine:v3.17: `putty` — affected >=0 <0.73-r0
- Alpine:v3.18: `putty` — affected >=0 <0.73-r0
- Alpine:v3.19: `putty` — affected >=0 <0.73-r0
- Alpine:v3.8: `putty` — affected >=0 <0.73-r0
- Alpine:v3.9: `putty` — affected >=0 <0.73-r0

## Details
PuTTY before 0.73 might allow remote SSH-1 servers to cause a denial of service by accessing freed memory locations via an SSH1_MSG_DISCONNECT message.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17069
