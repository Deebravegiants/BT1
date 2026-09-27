# [M] PostgreSQL CREATE TYPE does not check multirange schema CREATE privilege

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-6472
Aliases: CVE-2026-6472
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6472
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Missing authorization in PostgreSQL CREATE TYPE allows an object creator to hijack other queries that use search_path to find user-defined types, including extension-defined types.  That is to say, the victim will execute arbitrary SQL functions of the attacker's choice.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6472
- https://www.postgresql.org/support/security/CVE-2026-6472/
