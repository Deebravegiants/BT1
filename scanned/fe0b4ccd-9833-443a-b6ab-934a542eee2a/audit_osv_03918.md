# [H] ALPINE-CVE-2026-6476

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6476
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6476
Type: osv

## Affected
- Alpine:v3.21: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.4-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.4-r0

## Details
SQL injection in PostgreSQL pg_createsubscriber allows an attacker with pg_create_subscription rights to execute arbitrary SQL as a superuser.  The attack takes effect when pg_createsubscriber next runs.  Within major versions 17 and 18, minor versions before PostgreSQL 18.4 and 17.10 are affected.  Versions before PostgreSQL 17 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6476
