# [H] PostgreSQL refint plan cache type confusion executes arbitrary code

## Summary
Severity: High
Advisory: BIT-postgresql-2026-14671
Aliases: CVE-2026-14671
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14671
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Type confusion in PostgreSQL module "refint" allows an object creator to execute arbitrary code as the operating system user running the database.  The fix for this emerged as a non-security bug report, and the fix appear in the git repository with subject "refint: Remove plan cache.", without a CVE number.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14671
- https://www.postgresql.org/support/security/CVE-2026-14671/
