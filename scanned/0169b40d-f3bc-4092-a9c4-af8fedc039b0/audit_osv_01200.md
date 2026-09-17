# [H] ALPINE-CVE-2018-5733

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5733
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5733
Type: osv

## Affected
- Alpine:v3.10: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.11: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.12: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.13: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.14: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.15: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.16: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.17: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.18: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.19: `dhcp` — affected >=4.2.0 <4.4.1-r0
- Alpine:v3.20: `dhcp` — affected >=4.2.0 <4.4.1-r0

## Details
A malicious client which is allowed to send very large amounts of traffic (billions of packets) to a DHCP server can eventually overflow a 32-bit reference counter, potentially causing dhcpd to crash. Affects ISC DHCP 4.1.0 -> 4.1-ESV-R15, 4.2.0 -> 4.2.8, 4.3.0 -> 4.3.6, 4.4.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5733
