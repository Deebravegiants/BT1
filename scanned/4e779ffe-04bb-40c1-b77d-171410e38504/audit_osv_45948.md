# [M] JLSEC-2026-51

## Summary
Severity: Medium
Advisory: JLSEC-2026-51
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-51
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=14.1.0+0 <16.8.0+0

## Details
Missing authorization in PostgreSQL built-in views `pg_stats_ext` and `pg_stats_ext_exprs` allows an unprivileged database user to read most common values and other statistics from CREATE STATISTICS commands of other users. The most common values may reveal column values the eavesdropper could not otherwise read or results of functions they cannot execute. Installing an unaffected version only fixes fresh PostgreSQL installations, namely those that are created with the initdb utility after installing that version. Current PostgreSQL installations will remain vulnerable until they follow the instructions in the release notes. Within major versions 14-16, minor versions before PostgreSQL 16.3, 15.7, and 14.12 are affected. Versions before PostgreSQL 14 are unaffected.

## References
- https://security.netapp.com/advisory/ntap-20250328-0001/
- https://www.postgresql.org/support/security/CVE-2024-4317/
