# [M] PostgreSQL pg_restore_attribute_stats accepts values that cause query planning to read past end of stats array

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-6575
Aliases: CVE-2026-6575
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6575
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Buffer over-read in PostgreSQL function pg_restore_attribute_stats() accepts array values of unmatched length, which causes query planning to read past end of one array.  This allows a table maintainer to infer memory values past that array end.  Within major version 18, minor versions before PostgreSQL 18.4 are affected.  Versions before PostgreSQL 18 are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6575
- https://www.postgresql.org/support/security/CVE-2026-6575/
