# [H] ALPINE-CVE-2018-8740

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-8740
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-8740
Type: osv

## Affected
- Alpine:v3.4: `sqlite` — affected >=0 <3.13.0-r2
- Alpine:v3.5: `sqlite` — affected >=0 <3.15.2-r2
- Alpine:v3.6: `sqlite` — affected >=0 <3.20.1-r2
- Alpine:v3.7: `sqlite` — affected >=0 <3.21.0-r1

## Details
In SQLite through 3.22.0, databases whose schema is corrupted using a CREATE TABLE AS statement could cause a NULL pointer dereference, related to build.c and prepare.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-8740
