# [M] ALPINE-CVE-2018-18409

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-18409
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18409
Type: osv

## Affected
- Alpine:v3.10: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.11: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.12: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.13: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.14: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.15: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.16: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.17: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.18: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.19: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.20: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.21: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.22: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.23: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.24: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.7: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.8: `tcpflow` — affected >=0 <1.5.0-r1
- Alpine:v3.9: `tcpflow` — affected >=0 <1.5.0-r1

## Details
A stack-based buffer over-read exists in setbit() at iptree.h of TCPFLOW 1.5.0, due to received incorrect values causing incorrect computation, leading to denial of service during an address_histogram call or a get_histogram call.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18409
