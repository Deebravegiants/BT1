# [M] PostgreSQL pg_trgm picksplit reads past end of buffer

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-14678
Aliases: CVE-2026-14678
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14678
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Buffer over-read in PostgreSQL pg_trgm index picksplit function reads past end of a heap buffer.  This might allow a table maintainer to infer limited memory values, via the lossy signal of index split choices.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14678
- https://www.postgresql.org/support/security/CVE-2026-14678/
