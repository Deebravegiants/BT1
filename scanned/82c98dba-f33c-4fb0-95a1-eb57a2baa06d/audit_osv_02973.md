# [H] ALPINE-CVE-2024-11187

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-11187
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-11187
Type: osv

## Affected
- Alpine:v3.18: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.19: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.22: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.23: `bind` — affected >=0 <9.18.33-r0
- Alpine:v3.24: `bind` — affected >=0 <9.18.33-r0

## Details
It is possible to construct a zone such that some queries to it will generate responses containing numerous records in the Additional section. An attacker sending many such queries can cause either the authoritative server itself or an independent resolver to use disproportionate resources processing the queries. Zones will usually need to have been deliberately crafted to attack this exposure.
This issue affects BIND 9 versions 9.11.0 through 9.11.37, 9.16.0 through 9.16.50, 9.18.0 through 9.18.32, 9.20.0 through 9.20.4, 9.21.0 through 9.21.3, 9.11.3-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.50-S1, and 9.18.11-S1 through 9.18.32-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-11187
