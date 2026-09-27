# [H] ALPINE-CVE-2019-18679

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18679
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18679
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=2.0 <4.8-r1
- Alpine:v3.11: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.12: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.13: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.14: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.15: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.16: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.17: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.18: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.19: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.20: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.21: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.22: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.23: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.24: `squid` — affected >=2.0 <4.9-r0
- Alpine:v3.9: `squid` — affected >=2.0 <4.8-r1

## Details
An issue was discovered in Squid 2.x, 3.x, and 4.x through 4.8. Due to incorrect data management, it is vulnerable to information disclosure when processing HTTP Digest Authentication. Nonce tokens contain the raw byte value of a pointer that sits within heap memory allocation. This information reduces ASLR protections and may aid attackers isolating memory areas to target for remote code execution attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18679
