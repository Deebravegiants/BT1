# [H] PostgreSQL pg_createsubscriber allows SQL injection via subscription name

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6476
Aliases: CVE-2026-6476
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6476
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
SQL injection in PostgreSQL pg_createsubscriber allows an attacker with pg_create_subscription rights to execute arbitrary SQL as a superuser.  The attack takes effect when pg_createsubscriber next runs.  Within major versions 17 and 18, minor versions before PostgreSQL 18.4 and 17.10 are affected.  Versions before PostgreSQL 17 are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6476
- https://www.postgresql.org/support/security/CVE-2026-6476/
