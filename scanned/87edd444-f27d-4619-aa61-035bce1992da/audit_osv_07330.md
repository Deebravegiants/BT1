# [M] PostgreSQL pg_stats_ext and pg_stats_ext_exprs lack authorization checks

## Summary
Severity: Medium
Advisory: BIT-postgresql-2024-4317
Aliases: CVE-2024-4317
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-postgresql-2024-4317
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=16.0.0 <16.3.0

## Details
Missing authorization in PostgreSQL built-in views pg_stats_ext and pg_stats_ext_exprs allows an unprivileged database user to read most common values and other statistics from CREATE STATISTICS commands of other users. The most common values may reveal column values the eavesdropper could not otherwise read or results of functions they cannot execute. Installing an unaffected version only fixes fresh PostgreSQL installations, namely those that are created with the initdb utility after installing that version. Current PostgreSQL installations will remain vulnerable until they follow the instructions in the release notes. Within major versions 14-16, minor versions before PostgreSQL 16.3, 15.7, and 14.12 are affected. Versions before PostgreSQL 14 are unaffected.

## References
- https://www.postgresql.org/support/security/CVE-2024-4317/
- https://security.netapp.com/advisory/ntap-20250328-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2024-4317
