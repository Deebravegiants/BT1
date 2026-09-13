# [M] PostgreSQL libpq undersizes allocations, via integer wraparound

## Summary
Severity: Medium
Advisory: BIT-postgresql-2025-12818
Aliases: CVE-2025-12818
Ecosystem: Bitnami
Published: 2025-11-21
Source: https://osv.dev/vulnerability/BIT-postgresql-2025-12818
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.1.0

## Details
Integer wraparound in multiple PostgreSQL libpq client library functions allows an application input provider or network peer to cause libpq to undersize an allocation and write out-of-bounds by hundreds of megabytes.  This results in a segmentation fault for the application using libpq.  Versions before PostgreSQL 18.1, 17.7, 16.11, 15.15, 14.20, and 13.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12818
- https://www.postgresql.org/support/security/CVE-2025-12818/
