# [H] ALPINE-CVE-2026-16238

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-16238
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-16238
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
Type confusion in PostgreSQL pg_restore_attribute_stats() allows an object creator to execute arbitrary code as the operating system user running the database, via conflation of range and multirange values.  Within major version 18, minor versions before PostgreSQL 18.6 are affected.  Versions before PostgreSQL 18 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-16238
