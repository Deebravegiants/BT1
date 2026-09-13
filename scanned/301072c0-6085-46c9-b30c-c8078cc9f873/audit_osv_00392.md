# [H] ALPINE-CVE-2017-11108

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11108
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11108
Type: osv

## Affected
- Alpine:v3.10: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.11: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.12: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.13: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.14: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.15: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.16: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.17: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.18: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.19: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.20: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.21: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.22: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.23: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.24: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.3: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.4: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.5: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.6: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.7: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.8: `tcpdump` — affected >=0 <4.9.1-r0
- Alpine:v3.9: `tcpdump` — affected >=0 <4.9.1-r0

## Details
tcpdump 4.9.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via crafted packet data. The crash occurs in the EXTRACT_16BITS function, called from the stp_print function for the Spanning Tree Protocol.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11108
