# [H] PostgreSQL 32-bit pltcl and plperl undersize allocations, via integer wraparound

## Summary
Severity: High
Advisory: BIT-postgresql-2026-14677
Aliases: CVE-2026-14677
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14677
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Integer wraparound in PostgreSQL 32-bit builds of pltcl and plperl allows an object creator to cause the server to undersize an allocation and write out-of-bounds via crafted function bodies.  This may execute arbitrary code as the operating system user running the database.  CVE-2026-6473 had fixed similar problems.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14677
- https://www.postgresql.org/support/security/CVE-2026-14677/
