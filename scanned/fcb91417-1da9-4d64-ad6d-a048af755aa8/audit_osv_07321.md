# [M] Postgresql: merge fails to enforce update or select row security policies

## Summary
Severity: Medium
Advisory: BIT-postgresql-2023-39418
Aliases: CVE-2023-39418
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2023-39418
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=15.0.0 <15.4.0

## Details
A vulnerability was found in PostgreSQL with the use of the MERGE command, which fails to test new rows against row security policies defined for UPDATE and SELECT. If UPDATE and SELECT policies forbid some rows that INSERT policies do not forbid, a user could store such rows.

## References
- https://access.redhat.com/errata/RHSA-2023:7785
- https://access.redhat.com/errata/RHSA-2023:7883
- https://access.redhat.com/errata/RHSA-2023:7884
- https://access.redhat.com/errata/RHSA-2023:7885
- https://access.redhat.com/security/cve/CVE-2023-39418
- https://bugzilla.redhat.com/show_bug.cgi?id=2228112
- https://git.postgresql.org/gitweb/?p=postgresql.git;a=commitdiff;h=cb2ae5741f2458a474ed3c31458d242e678ff229
- https://security.netapp.com/advisory/ntap-20230915-0002/
- https://www.debian.org/security/2023/dsa-5553
- https://www.postgresql.org/support/security/CVE-2023-39418/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39418
