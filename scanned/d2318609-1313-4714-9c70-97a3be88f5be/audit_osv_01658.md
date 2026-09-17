# [C] ALPINE-CVE-2019-8457

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-8457
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-8457
Type: osv

## Affected
- Alpine:v3.10: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.11: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.12: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.13: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.14: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.15: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.16: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.17: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.18: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.19: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.20: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.21: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.22: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.23: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.24: `sqlite` — affected >=3.6.0 <3.28.0-r0
- Alpine:v3.7: `sqlite` — affected >=3.6.0 <3.25.3-r1
- Alpine:v3.8: `sqlite` — affected >=3.6.0 <3.25.3-r1
- Alpine:v3.9: `sqlite` — affected >=3.6.0 <3.28.0-r0

## Details
SQLite3 from 3.6.0 to and including 3.27.2 is vulnerable to heap out-of-bound read in the rtreenode() function when handling invalid rtree tables.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-8457
