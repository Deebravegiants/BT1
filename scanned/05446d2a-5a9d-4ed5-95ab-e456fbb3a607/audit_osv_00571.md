# [M] ALPINE-CVE-2017-16808

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-16808
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16808
Type: osv

## Affected
- Alpine:v3.10: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.11: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.12: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.13: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.14: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.15: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.16: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.17: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.18: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.19: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.20: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.21: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.22: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.23: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.24: `tcpdump` — affected >=0 <4.9.3-r0
- Alpine:v3.9: `tcpdump` — affected >=0 <4.9.3-r0

## Details
tcpdump before 4.9.3 has a heap-based buffer over-read related to aoe_print in print-aoe.c and lookup_emem in addrtoname.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16808
