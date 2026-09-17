# [H] ALPINE-CVE-2025-8714

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-8714
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-8714
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
Untrusted data inclusion in pg_dump in PostgreSQL allows a malicious superuser of the origin server to inject arbitrary code for restore-time execution as the client operating system account running psql to restore the dump, via psql meta-commands.  pg_dumpall is also affected.  pg_restore is affected when used to generate a plain-format dump.  This is similar to MySQL CVE-2024-21096.  Versions before PostgreSQL 17.6, 16.10, 15.14, 14.19, and 13.22 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-8714
