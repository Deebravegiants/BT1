# [H] PostgreSQL pg_dump lets superuser of origin server execute arbitrary code in psql client

## Summary
Severity: High
Advisory: BIT-postgresql-2025-8714
Aliases: CVE-2025-8714
Ecosystem: Bitnami
Published: 2025-08-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2025-8714
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=17.0.0 <17.6.0

## Details
Untrusted data inclusion in pg_dump in PostgreSQL allows a malicious superuser of the origin server to inject arbitrary code for restore-time execution as the client operating system account running psql to restore the dump, via psql meta-commands.  pg_dumpall is also affected.  pg_restore is affected when used to generate a plain-format dump.  This is similar to MySQL CVE-2024-21096.  Versions before PostgreSQL 17.6, 16.10, 15.14, 14.19, and 13.22 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8714
- https://www.postgresql.org/support/security/CVE-2025-8714/
