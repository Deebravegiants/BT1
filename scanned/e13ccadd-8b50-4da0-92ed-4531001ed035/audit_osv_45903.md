# [H] JLSEC-2026-46

## Summary
Severity: High
Advisory: JLSEC-2026-46
Ecosystem: Julia
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-46
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.0.0+0

## Details
Late privilege drop in REFRESH MATERIALIZED VIEW CONCURRENTLY in PostgreSQL allows an object creator to execute arbitrary SQL functions as the command issuer. The command intends to run SQL functions as the owner of the materialized view, enabling safe refresh of untrusted materialized views. The victim is a superuser or member of one of the attacker's roles. The attack requires luring the victim into running REFRESH MATERIALIZED VIEW CONCURRENTLY on the attacker's materialized view. Versions before PostgreSQL 16.2, 15.6, 14.11, 13.14, and 12.18 are affected.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00017.html
- https://saites.dev/projects/personal/postgres-cve-2024-0985/
- https://security.netapp.com/advisory/ntap-20241220-0005/
- https://www.postgresql.org/support/security/CVE-2024-0985/
