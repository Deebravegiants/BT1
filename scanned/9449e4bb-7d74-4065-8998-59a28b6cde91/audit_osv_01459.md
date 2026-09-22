# [C] ALPINE-CVE-2019-15167

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-15167
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15167
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
The VRRP parser in tcpdump before 4.9.3 has a buffer over-read in print-vrrp.c:vrrp_print() for VRRP version 3, a different vulnerability than CVE-2018-14463.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15167
