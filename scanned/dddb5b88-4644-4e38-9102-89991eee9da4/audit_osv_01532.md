# [H] ALPINE-CVE-2019-19244

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19244
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19244
Type: osv

## Affected
- Alpine:v3.10: `sqlite` — affected >=0 <3.28.0-r2
- Alpine:v3.11: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.12: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.13: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.14: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.15: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.16: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.17: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.18: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.19: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.20: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.21: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.22: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.23: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.24: `sqlite` — affected >=0 <3.30.1-r1
- Alpine:v3.8: `sqlite` — affected >=0 <3.25.3-r3
- Alpine:v3.9: `sqlite` — affected >=0 <3.28.0-r2

## Details
sqlite3Select in select.c in SQLite 3.30.1 allows a crash if a sub-select uses both DISTINCT and window functions, and also has certain ORDER BY usage.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19244
