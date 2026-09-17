# [M] PostgreSQL row security caching disregards role modifications

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-14666
Aliases: CVE-2026-14666
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14666
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Incomplete tracking in PostgreSQL of changes to role membership, role attributes, and database ownership allows a query to continue using cached row-level security policies after those changes require a different policy, via plan reuse.  Stale policies continue until some other event invalidates the cache or connection termination ends the session.  This permits a user to complete reads and modifications that were recently permitted but now forbidden.  An attacker must tailor an attack to a particular application's pattern of privilege removal and role-specific row security policies.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14666
- https://www.postgresql.org/support/security/CVE-2026-14666/
