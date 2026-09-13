# [M] PostgreSQL ascii() function reads past end of buffer

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-18024
Aliases: CVE-2026-18024
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-18024
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Buffer over-read in PostgreSQL ascii() SQL function allows a user to disclose up to 3 bytes after the end of a specific allocation, via a crafted text value.  This is the same class of defect that CVE-2026-2006 fixed, though this instance has less impact.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-18024
- https://www.postgresql.org/support/security/CVE-2026-18024/
