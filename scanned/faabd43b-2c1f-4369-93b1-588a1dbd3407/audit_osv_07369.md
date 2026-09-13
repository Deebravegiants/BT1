# [H] PostgreSQL refint allows stack buffer overflow and SQL injection

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6637
Aliases: CVE-2026-6637
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6637
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Stack buffer overflow in PostgreSQL module "refint" allows an unprivileged database user to execute arbitrary code as the operating system user running the database.  A distinct attack is possible if the application declares a user-controlled column as a "refint" cascade primary key and facilitates user-controlled updates to that column.  In that case, a SQL injection allows a primary key update value provider to execute arbitrary SQL as the database user performing the primary key update.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6637
- https://www.postgresql.org/support/security/CVE-2026-6637/
