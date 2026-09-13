# [H] ALPINE-CVE-2024-1737

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-1737
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-1737
Type: osv

## Affected
- Alpine:v3.17: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.18: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.19: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.28-r0
- Alpine:v3.22: `bind` — affected >=0 <9.18.28-r0
- Alpine:v3.23: `bind` — affected >=0 <9.18.28-r0
- Alpine:v3.24: `bind` — affected >=0 <9.18.28-r0

## Details
Resolver caches and authoritative zone databases that hold significant numbers of RRs for the same hostname (of any RTYPE) can suffer from degraded performance as content is being added or updated, and also when handling client queries for this name.
This issue affects BIND 9 versions 9.11.0 through 9.11.37, 9.16.0 through 9.16.50, 9.18.0 through 9.18.27, 9.19.0 through 9.19.24, 9.11.4-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.50-S1, and 9.18.11-S1 through 9.18.27-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-1737
