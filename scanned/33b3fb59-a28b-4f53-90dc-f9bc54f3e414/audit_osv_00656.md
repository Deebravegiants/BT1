# [C] ALPINE-CVE-2017-5342

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-5342
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5342
Type: osv

## Affected
- Alpine:v3.10: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.11: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.12: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.13: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.14: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.15: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.16: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.17: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.18: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.19: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.2: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.20: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.21: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.22: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.23: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.24: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.3: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.4: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.5: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.6: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.7: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.8: `tcpdump` — affected >=0 <4.9.0-r0
- Alpine:v3.9: `tcpdump` — affected >=0 <4.9.0-r0

## Details
In tcpdump before 4.9.0, a bug in multiple protocol parsers (Geneve, GRE, NSH, OTV, VXLAN and VXLAN GPE) could cause a buffer overflow in print-ether.c:ether_print().

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5342
