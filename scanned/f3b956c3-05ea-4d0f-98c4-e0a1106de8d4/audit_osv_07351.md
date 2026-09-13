# [H] PostgreSQL type confusion in cursor CLOSE + DECLARE executes arbitrary code

## Summary
Severity: High
Advisory: BIT-postgresql-2026-16239
Aliases: CVE-2026-16239
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-16239
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Type confusion in PostgreSQL "portal"/cursor lifecycle allows a user to execute arbitrary code as the operating system user running the database, via re-creation of a cursor or other portal with different types.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-16239
- https://www.postgresql.org/support/security/CVE-2026-16239/
