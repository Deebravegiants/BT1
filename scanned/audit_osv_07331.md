# [H] PostgreSQL relation replacement during pg_dump executes arbitrary SQL

## Summary
Severity: High
Advisory: BIT-postgresql-2024-7348
Aliases: CVE-2024-7348
Ecosystem: Bitnami
Published: 2024-08-10
Source: https://osv.dev/vulnerability/BIT-postgresql-2024-7348
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=16.0.0 <16.4.0

## Details
Time-of-check Time-of-use (TOCTOU) race condition in pg_dump in PostgreSQL allows an object creator to execute arbitrary SQL functions as the user running pg_dump, which is often a superuser. The attack involves replacing another relation type with a view or foreign table. The attack requires waiting for pg_dump to start, but winning the race condition is trivial if the attacker retains an open transaction. Versions before PostgreSQL 16.4, 15.8, 14.13, 13.16, and 12.20 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2024-7348/
- http://www.openwall.com/lists/oss-security/2024/08/11/1
- https://security.netapp.com/advisory/ntap-20240822-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2024-7348
