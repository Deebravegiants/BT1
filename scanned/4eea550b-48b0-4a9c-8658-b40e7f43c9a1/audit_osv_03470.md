# [H] ALPINE-CVE-2026-15741

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-15741
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-15741
Type: osv

## Affected
- Alpine:v3.21: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.5-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.5-r0

## Details
SQL injection in PostgreSQL EXTRACT() deparse allows an object owner to execute arbitrary SQL as a superuser via a hostile object definition.  Attacks affect expression deparse consumers broadly, including pg_dump, psql commands like \sf, and any similar usage in non-core tools.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-15741
