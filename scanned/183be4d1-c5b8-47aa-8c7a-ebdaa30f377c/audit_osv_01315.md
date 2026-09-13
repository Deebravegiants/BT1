# [M] ALPINE-CVE-2019-10130

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10130
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10130
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.5.0 <11.3-r0
- Alpine:v3.11: `postgresql` — affected >=9.5.0 <11.3-r0
- Alpine:v3.12: `postgresql` — affected >=9.5.0 <11.3-r0
- Alpine:v3.13: `postgresql` — affected >=9.5.0 <11.3-r0
- Alpine:v3.14: `postgresql` — affected >=9.5.0 <11.3-r0
- Alpine:v3.6: `postgresql` — affected >=9.5.0 <9.6.13-r0
- Alpine:v3.7: `postgresql` — affected >=9.5.0 <10.8-r0
- Alpine:v3.8: `postgresql` — affected >=9.5.0 <10.8-r0
- Alpine:v3.9: `postgresql` — affected >=9.5.0 <11.3-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <11.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <11.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <11.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <11.3-r0

## Details
A vulnerability was found in PostgreSQL versions 11.x up to excluding 11.3, 10.x up to excluding 10.8, 9.6.x up to, excluding 9.6.13, 9.5.x up to, excluding 9.5.17. PostgreSQL maintains column statistics for tables. Certain statistics, such as histograms and lists of most common values, contain values taken from the column. PostgreSQL does not evaluate row security policies before consulting those statistics during query planning; an attacker can exploit this to read the most common values of certain columns. Affected columns are those for which the attacker has SELECT privilege and for which, in an ordinary query, row-level security prunes the set of rows visible to the attacker.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10130
