# [H] PostgreSQL type confusion via "internal" arguments

## Summary
Severity: High
Advisory: BIT-postgresql-2026-14680
Aliases: CVE-2026-14680
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14680
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Type confusion with PostgreSQL "internal" data type arguments allows any user to execute arbitrary code as the operating system user running the database, via calls to functions with that argument type.  Type "internal" represents a class of mutually-incompatible data structures not intended for access from SQL.  The system intended to prevent such function calls, but this prevention had gaps.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14680
- https://www.postgresql.org/support/security/CVE-2026-14680/
