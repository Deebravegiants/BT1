# [H] ALPINE-CVE-2020-14349

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14349
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14349
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=10.0 <11.9-r0
- Alpine:v3.11: `postgresql` — affected >=10.0 <12.4-r0
- Alpine:v3.12: `postgresql` — affected >=10.0 <12.4-r0
- Alpine:v3.13: `postgresql` — affected >=10.0 <12.4-r0
- Alpine:v3.14: `postgresql` — affected >=10.0 <12.4-r0
- Alpine:v3.9: `postgresql` — affected >=10.0 <11.9-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <12.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <12.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <12.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <12.4-r0

## Details
It was found that PostgreSQL versions before 12.4, before 11.9 and before 10.14 did not properly sanitize the search_path during logical replication. An authenticated attacker could use this flaw in an attack similar to CVE-2018-1058, in order to execute arbitrary SQL command in the context of the user used for replication.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14349
