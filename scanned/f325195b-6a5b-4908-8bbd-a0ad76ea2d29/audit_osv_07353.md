# [M] PostgreSQL oidvector discloses a few bytes of memory

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-2003
Aliases: CVE-2026-2003
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-2003
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.2.0

## Details
Improper validation of type "oidvector" in PostgreSQL allows a database user to disclose a few bytes of server memory.  We have not ruled out viability of attacks that arrange for presence of confidential information in disclosed bytes, but they seem unlikely.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2003
- https://www.postgresql.org/support/security/CVE-2026-2003/
