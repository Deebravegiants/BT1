# [C] ALPINE-CVE-2023-49606

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-49606
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49606
Type: osv

## Affected
- Alpine:v3.16: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.17: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.18: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.19: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.20: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.21: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.22: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.23: `tinyproxy` — affected >=0 <1.11.2-r0
- Alpine:v3.24: `tinyproxy` — affected >=0 <1.11.2-r0

## Details
A use-after-free vulnerability exists in the HTTP Connection Headers parsing in Tinyproxy 1.11.1 and Tinyproxy 1.10.0. A specially crafted HTTP header can trigger reuse of previously freed memory, which leads to memory corruption and could lead to remote code execution. An attacker needs to make an unauthenticated HTTP request to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49606
