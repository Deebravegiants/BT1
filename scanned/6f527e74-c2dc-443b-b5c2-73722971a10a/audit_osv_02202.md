# [M] ALPINE-CVE-2021-31810

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-31810
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2021-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-31810
Type: osv

## Affected
- Alpine:v3.11: `ruby` — affected >=2.7.0 <2.6.8-r0
- Alpine:v3.12: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.13: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.14: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.15: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.16: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.17: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.18: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.19: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.20: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.21: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.22: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.23: `ruby` — affected >=2.7.0 <2.7.4-r0
- Alpine:v3.24: `ruby` — affected >=2.7.0 <2.7.4-r0

## Details
An issue was discovered in Ruby through 2.6.7, 2.7.x through 2.7.3, and 3.x through 3.0.1. A malicious FTP server can use the PASV response to trick Net::FTP into connecting back to a given IP address and port. This potentially makes curl extract information about services that are otherwise private and not disclosed (e.g., the attacker can conduct port scans and service banner extractions).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-31810
