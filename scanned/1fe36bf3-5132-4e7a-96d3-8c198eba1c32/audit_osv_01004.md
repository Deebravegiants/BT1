# [C] ALPINE-CVE-2018-14938

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-14938
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14938
Type: osv

## Affected
- Alpine:v3.11: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.12: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.13: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.14: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.15: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.16: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.17: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.18: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.19: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.20: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.21: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.22: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.23: `tcpflow` — affected >=0 <1.5.0-r0
- Alpine:v3.24: `tcpflow` — affected >=0 <1.5.0-r0

## Details
An issue was discovered in wifipcap/wifipcap.cpp in TCPFLOW through 1.5.0-alpha. There is an integer overflow in the function handle_prism during caplen processing. If the caplen is less than 144, one can cause an integer overflow in the function handle_80211, which will result in an out-of-bounds read and may allow access to sensitive memory (or a denial of service).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14938
