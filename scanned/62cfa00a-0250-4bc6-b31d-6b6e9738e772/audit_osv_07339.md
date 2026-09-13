# [H] PostgreSQL regexp heap buffer overflow executes arbitrary code

## Summary
Severity: High
Advisory: BIT-postgresql-2026-14664
Aliases: CVE-2026-14664
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14664
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Heap buffer overflow in PostgreSQL regexp allows the query author to execute arbitrary code as the operating system user running the database, via text that would not pass encoding validation.  This shares heritage with CVE-2026-2006, but this case involved unanticipated data growth when round-tripped through pg_wchar.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14664
- https://www.postgresql.org/support/security/CVE-2026-14664/
