# [H] ALPINE-CVE-2025-8715

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-8715
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-8715
Type: osv

## Affected
- Alpine:v3.19: `postgresql15` — affected >=0 <15.14-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.14-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.10-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.10-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.10-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.10-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.6-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.6-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.6-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.6-r0

## Details
Improper neutralization of newlines in pg_dump in PostgreSQL allows a user of the origin server to inject arbitrary code for restore-time execution as the client operating system account running psql to restore the dump, via psql meta-commands inside a purpose-crafted object name.  The same attacks can achieve SQL injection as a superuser of the restore target server.  pg_dumpall, pg_restore, and pg_upgrade are also affected.  Versions before PostgreSQL 17.6, 16.10, 15.14, 14.19, and 13.22 are affected.  Versions before 11.20 are unaffected.  CVE-2012-0868 had fixed this class of problem, but version 11.20 reintroduced it.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-8715
