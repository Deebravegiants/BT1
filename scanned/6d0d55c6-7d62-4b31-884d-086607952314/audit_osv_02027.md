# [M] ALPINE-CVE-2020-8619

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8619
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8619
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.11: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.12: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.13: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.14: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.15: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.16: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.17: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.18: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.19: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.20: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.21: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.22: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.23: `bind` — affected >=9.11.14 <9.16.4-r0
- Alpine:v3.24: `bind` — affected >=9.11.14 <9.16.4-r0

## Details
In ISC BIND9 versions BIND 9.11.14 -> 9.11.19, BIND 9.14.9 -> 9.14.12, BIND 9.16.0 -> 9.16.3, BIND Supported Preview Edition 9.11.14-S1 -> 9.11.19-S1: Unless a nameserver is providing authoritative service for one or more zones and at least one zone contains an empty non-terminal entry containing an asterisk ("*") character, this defect cannot be encountered. A would-be attacker who is allowed to change zone content could theoretically introduce such a record in order to exploit this condition to cause denial of service, though we consider the use of this vector unlikely because any such attack would require a significant privilege level and be easily traceable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8619
