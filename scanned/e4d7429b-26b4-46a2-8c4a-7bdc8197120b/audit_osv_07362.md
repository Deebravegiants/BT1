# [M] PostgreSQL timeofday() can disclose portions of server memory

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-6474
Aliases: CVE-2026-6474
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6474
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Externally-controlled format string in PostgreSQL timeofday() function allows an attacker to retrieve portions of server memory, via crafted timezone zones.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6474
- https://www.postgresql.org/support/security/CVE-2026-6474/
