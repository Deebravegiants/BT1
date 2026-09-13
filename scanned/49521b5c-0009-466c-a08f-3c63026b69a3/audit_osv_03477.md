# [H] ALPINE-CVE-2026-18408

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-18408
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-18408
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
Untrusted data inclusion in pg_dump in PostgreSQL allows a malicious superuser of the origin server to inject arbitrary code for restore-time execution as the client operating system account running psql to restore the dump, via psql \restrict meta-command input expansion.  The fix for CVE-2025-8714 introduced \restrict and \unrestrict to block this attack, but \unrestrict itself was sufficient for an attack.  pg_dumpall is also affected.  pg_restore is affected when used to generate a plain-format dump.  Non-core use of \restrict would be affected, but we've not identified non-core use.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-18408
