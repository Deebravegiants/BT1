# [H] PostgreSQL fuzzystrmatch writes effectively-arbitrary addresses, via integer wraparound

## Summary
Severity: High
Advisory: BIT-postgresql-2026-15742
Aliases: CVE-2026-15742
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-15742
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Integer wraparound in PostgreSQL fuzzystrmatch allows a user to direct writes to a huge range of addresses, executing arbitrary code as the operating system user running the database, via extreme inputs to SQL function levenshtein() or levenshtein_less_equal().  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-15742
- https://www.postgresql.org/support/security/CVE-2026-15742/
