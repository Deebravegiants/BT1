# [M] BIT-postgresql-2023-2455

## Summary
Severity: Medium
Advisory: BIT-postgresql-2023-2455
Aliases: CVE-2023-2455
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2023-2455
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=15.0.0 <15.3.0

## Details
Row security policies disregard user ID changes after inlining; PostgreSQL could permit incorrect policies to be applied in certain cases where role-specific policies are used and a given query is planned under one role and then executed under other roles. This scenario can happen under security definer functions or when a common user and query is planned initially and then re-used across multiple SET ROLEs. Applying an incorrect policy may permit a user to complete otherwise-forbidden reads and modifications. This affects only databases that have used CREATE POLICY to define a row security policy.

## References
- https://access.redhat.com/security/cve/CVE-2023-2455
- https://security.netapp.com/advisory/ntap-20230706-0006/
- https://www.postgresql.org/support/security/CVE-2023-2455/
- https://nvd.nist.gov/vuln/detail/CVE-2023-2455
