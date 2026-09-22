# [H] PostgreSQL REFRESH PUBLICATION allows SQL injection via table name

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6638
Aliases: CVE-2026-6638
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6638
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
SQL injection in PostgreSQL logical replication ALTER SUBSCRIPTION ... REFRESH PUBLICATION allows a subscriber table creator to execute arbitrary SQL with the subscription's publication-side credentials.  The attack takes effect at the next REFRESH PUBLICATION.  Within major versions 16, 17, and 18, minor versions before PostgreSQL 18.4, 17.10, and 16.14 are affected.  Versions before PostgreSQL 16 are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6638
- https://www.postgresql.org/support/security/CVE-2026-6638/
