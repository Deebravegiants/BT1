# [M] ALPINE-CVE-2019-16168

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-16168
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-16168
Type: osv

## Affected
- Alpine:v3.10: `sqlite` — affected >=3.8.5 <3.28.0-r1
- Alpine:v3.8: `sqlite` — affected >=3.8.5 <3.25.3-r2
- Alpine:v3.9: `sqlite` — affected >=3.8.5 <3.28.0-r1

## Details
In SQLite through 3.29.0, whereLoopAddBtreeIndex in sqlite3.c can crash a browser or other application because of missing validation of a sqlite_stat1 sz field, aka a "severe division by zero in the query planner."

## References
- https://security.alpinelinux.org/vuln/CVE-2019-16168
