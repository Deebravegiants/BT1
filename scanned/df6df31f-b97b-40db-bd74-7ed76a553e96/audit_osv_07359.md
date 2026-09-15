# [H] PostgreSQL logical decoding can dlopen arbitrary file

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6471
Aliases: CVE-2026-6471
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6471
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Missing authorization in PostgreSQL logical decoding allows a non-superuser holding REPLICATION privilege to dlopen any file visible to the operating system account running the server, via the choice of logical decoding plugin.  This in turn runs arbitrary code as that account.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6471
- https://www.postgresql.org/support/security/CVE-2026-6471/
