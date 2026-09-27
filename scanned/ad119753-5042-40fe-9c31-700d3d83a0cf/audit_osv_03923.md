# [M] ALPINE-CVE-2026-6575

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-6575
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6575
Type: osv

## Affected
- Alpine:v3.23: `postgresql18` — affected >=0 <18.4-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.4-r0

## Details
Buffer over-read in PostgreSQL function pg_restore_attribute_stats() accepts array values of unmatched length, which causes query planning to read past end of one array.  This allows a table maintainer to infer memory values past that array end.  Within major version 18, minor versions before PostgreSQL 18.4 are affected.  Versions before PostgreSQL 18 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6575
