# [M] JLSEC-2026-41

## Summary
Severity: Medium
Advisory: JLSEC-2026-41
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-41
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.0.0+0

## Details
Row security policies disregard user ID changes after inlining; PostgreSQL could permit incorrect policies to be applied in certain cases where role-specific policies are used and a given query is planned under one role and then executed under other roles. This scenario can happen under security definer functions or when a common user and query is planned initially and then re-used across multiple SET ROLEs. Applying an incorrect policy may permit a user to complete otherwise-forbidden reads and modifications. This affects only databases that have used CREATE POLICY to define a row security policy.

## References
- https://access.redhat.com/security/cve/CVE-2023-2455
- https://security.netapp.com/advisory/ntap-20230706-0006/
- https://www.postgresql.org/support/security/CVE-2023-2455/
