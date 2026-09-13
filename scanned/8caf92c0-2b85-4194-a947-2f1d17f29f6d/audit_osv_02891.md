# [H] ALPINE-CVE-2023-4408

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-4408
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4408
Type: osv

## Affected
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.16.48-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.18.24-r0

## Details
The DNS message parsing code in `named` includes a section whose computational complexity is overly high. It does not cause problems for typical DNS traffic, but crafted queries and responses may cause excessive CPU load on the affected `named` instance by exploiting this flaw. This issue affects both authoritative servers and recursive resolvers.
This issue affects BIND 9 versions 9.0.0 through 9.16.45, 9.18.0 through 9.18.21, 9.19.0 through 9.19.19, 9.9.3-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4408
