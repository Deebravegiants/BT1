# [H] PostgreSQL non-owner REFRESH MATERIALIZED VIEW CONCURRENTLY executes arbitrary SQL

## Summary
Severity: High
Advisory: BIT-postgresql-2024-0985
Aliases: CVE-2024-0985
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2024-0985
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=15.0.0 <15.6.0

## Details
Late privilege drop in REFRESH MATERIALIZED VIEW CONCURRENTLY in PostgreSQL allows an object creator to execute arbitrary SQL functions as the command issuer. The command intends to run SQL functions as the owner of the materialized view, enabling safe refresh of untrusted materialized views. The victim is a superuser or member of one of the attacker's roles. The attack requires luring the victim into running REFRESH MATERIALIZED VIEW CONCURRENTLY on the attacker's materialized view. Versions before PostgreSQL 16.2, 15.6, 14.11, 13.14, and 12.18 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2024-0985/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00017.html
- https://saites.dev/projects/personal/postgres-cve-2024-0985/
- https://security.netapp.com/advisory/ntap-20241220-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2024-0985
