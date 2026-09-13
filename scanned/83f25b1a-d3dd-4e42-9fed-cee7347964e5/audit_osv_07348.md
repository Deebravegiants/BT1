# [M] PostgreSQL improper enforcement of GSSAPI encryption when coupled with SSL

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-14681
Aliases: CVE-2026-14681
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14681
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Improper enforcement of message integrity in PostgreSQL GSSAPI support allows a user to negotiate GSSAPI contrary to pg_hba.conf rules, via initial direct TLS connection.  Despite a pg_hba.conf that appears to require GSSAPI, the connection may exchange data over TLS encryption alone.  If the TLS settings are more permissive than the GSS settings, the connection may continue with lesser protection.  Within major versions 17-18, minor versions before PostgreSQL 18.6 and 17.11 are affected.  Versions before PostgreSQL 17 are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14681
- https://www.postgresql.org/support/security/CVE-2026-14681/
