# [H] PostgreSQL pg_dump newline in object name executes arbitrary code in psql client and in restore target server

## Summary
Severity: High
Advisory: BIT-postgresql-2025-8715
Aliases: CVE-2025-8715
Ecosystem: Bitnami
Published: 2025-08-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2025-8715
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=17.0.0 <17.6.0

## Details
Improper neutralization of newlines in pg_dump in PostgreSQL allows a user of the origin server to inject arbitrary code for restore-time execution as the client operating system account running psql to restore the dump, via psql meta-commands inside a purpose-crafted object name.  The same attacks can achieve SQL injection as a superuser of the restore target server.  pg_dumpall, pg_restore, and pg_upgrade are also affected.  Versions before PostgreSQL 17.6, 16.10, 15.14, 14.19, and 13.22 are affected.  Versions before 11.20 are unaffected.  CVE-2012-0868 had fixed this class of problem, but version 11.20 reintroduced it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8715
- https://www.postgresql.org/support/security/CVE-2025-8715/
