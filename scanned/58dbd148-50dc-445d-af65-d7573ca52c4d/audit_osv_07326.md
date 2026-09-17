# [M] PostgreSQL row security below e.g. subqueries disregards user ID changes

## Summary
Severity: Medium
Advisory: BIT-postgresql-2024-10976
Aliases: CVE-2024-10976
Ecosystem: Bitnami
Published: 2024-11-16
Source: https://osv.dev/vulnerability/BIT-postgresql-2024-10976
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=17.0.0 <17.1.0

## Details
Incomplete tracking in PostgreSQL of tables with row security allows a reused query to view or change different rows from those intended.  CVE-2023-2455 and CVE-2016-2193 fixed most interaction between row security and user ID changes.  They missed cases where a subquery, WITH query, security invoker view, or SQL-language function references a table with a row-level security policy.  This has the same consequences as the two earlier CVEs.  That is to say, it leads to potentially incorrect policies being applied in cases where role-specific policies are used and a given query is planned under one role and then executed under other roles.  This scenario can happen under security definer functions or when a common user and query is planned initially and then re-used across multiple SET ROLEs.  Applying an incorrect policy may permit a user to complete otherwise-forbidden reads and modifications.  This affects only databases that have used CREATE POLICY to define a row security policy.  An attacker must tailor an attack to a particular application's pattern of query plan reuse, user ID changes, and role-specific row security policies.  Versions before PostgreSQL 17.1, 16.5, 15.9, 14.14, 13.17, and 12.21 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2024-10976/
- https://nvd.nist.gov/vuln/detail/CVE-2024-10976
- https://security.netapp.com/advisory/ntap-20250509-0010/
- https://lists.debian.org/debian-lts-announce/2024/11/msg00011.html
