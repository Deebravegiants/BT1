# [H] PostgreSQL expression deparse allows SQL injection via EXTRACT argument

## Summary
Severity: High
Advisory: BIT-postgresql-2026-15741
Aliases: CVE-2026-15741
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-15741
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
SQL injection in PostgreSQL EXTRACT() deparse allows an object owner to execute arbitrary SQL as a superuser via a hostile object definition.  Attacks affect expression deparse consumers broadly, including pg_dump, psql commands like \sf, and any similar usage in non-core tools.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-15741
- https://www.postgresql.org/support/security/CVE-2026-15741/
