# [H] JLSEC-2026-52

## Summary
Severity: High
Advisory: JLSEC-2026-52
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-52
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.8.0+0

## Details
Time-of-check Time-of-use (TOCTOU) race condition in `pg_dump` in PostgreSQL allows an object creator to execute arbitrary SQL functions as the user running `pg_dump`, which is often a superuser. The attack involves replacing another relation type with a view or foreign table. The attack requires waiting for `pg_dump` to start, but winning the race condition is trivial if the attacker retains an open transaction. Versions before PostgreSQL 16.4, 15.8, 14.13, 13.16, and 12.20 are affected.

## References
- http://www.openwall.com/lists/oss-security/2024/08/11/1
- https://security.netapp.com/advisory/ntap-20240822-0002/
- https://www.postgresql.org/support/security/CVE-2024-7348/
