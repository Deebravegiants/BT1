# [H] ALPINE-CVE-2018-16301

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16301
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16301
Type: osv

## Affected
- Alpine:v3.10: `libpcap` — affected >=0 <1.1.1-r0
- Alpine:v3.12: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.13: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.14: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.15: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.16: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.17: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.18: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.19: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.20: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.21: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.22: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.23: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.24: `libpcap` — affected >=0 <1.9.1-r0
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

## Details
The command-line argument parser in tcpdump before 4.99.0 has a buffer overflow in tcpdump.c:read_infile(). To trigger this vulnerability the attacker needs to create a 4GB file on the local filesystem and to specify the file name as the value of the -F command-line argument of tcpdump.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16301
