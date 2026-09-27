# [M] ALPINE-CVE-2023-28755

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-28755
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28755
Type: osv

## Affected
- Alpine:v3.14: `ruby` — affected >=0 <2.7.8-r0
- Alpine:v3.15: `ruby` — affected >=0 <3.0.6-r0
- Alpine:v3.16: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.17: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.18: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.19: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.20: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.22: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.23: `ruby` — affected >=0 <3.1.4-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.1.4-r0

## Details
A ReDoS issue was discovered in the URI component through 0.12.0 in Ruby through 3.2.1. The URI parser mishandles invalid URLs that have specific characters. It causes an increase in execution time for parsing strings to URI objects. The fixed versions are 0.12.1, 0.11.1, 0.10.2 and 0.10.0.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28755
