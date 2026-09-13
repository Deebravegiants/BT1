# [M] PostgreSQL GB18030 encoding validation can read one byte past end of allocation for text that fails validation

## Summary
Severity: Medium
Advisory: BIT-postgresql-2025-4207
Aliases: CVE-2025-4207
Ecosystem: Bitnami
Published: 2025-05-10
Source: https://osv.dev/vulnerability/BIT-postgresql-2025-4207
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=17.0.0 <17.5.0

## Details
Buffer over-read in PostgreSQL GB18030 encoding validation allows a database input provider to achieve temporary denial of service on platforms where a 1-byte over-read can elicit process termination.  This affects the database server and also libpq.  Versions before PostgreSQL 17.5, 16.9, 15.13, 14.18, and 13.21 are affected.

## References
- http://www.openwall.com/lists/oss-security/2025/05/09/3
- https://lists.debian.org/debian-lts-announce/2025/05/msg00011.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-4207
- https://www.postgresql.org/support/security/CVE-2025-4207/
