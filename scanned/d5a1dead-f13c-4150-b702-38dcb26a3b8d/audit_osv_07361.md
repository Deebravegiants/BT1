# [H] PostgreSQL server undersizes allocations, via integer wraparound

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6473
Aliases: CVE-2026-6473
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6473
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Integer wraparound in multiple PostgreSQL server features allows an unprivileged database user to cause the server to undersize an allocation and write out-of-bounds.  This may execute arbitrary code as the operating system user running the database.  In applications that pass gigabyte-scale user inputs to the relevant database functions, the application input provider may achieve a segmentation fault.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6473
- https://www.postgresql.org/support/security/CVE-2026-6473/
- https://access.redhat.com/errata/RHSA-2026:22878
- https://access.redhat.com/errata/RHSA-2026:26181
- https://access.redhat.com/errata/RHSA-2026:26203
- https://access.redhat.com/errata/RHSA-2026:26204
- https://access.redhat.com/errata/RHSA-2026:26524
- https://access.redhat.com/errata/RHSA-2026:26525
- https://access.redhat.com/errata/RHSA-2026:26561
- https://access.redhat.com/errata/RHSA-2026:27718
- https://access.redhat.com/errata/RHSA-2026:27738
- https://access.redhat.com/errata/RHSA-2026:27741
- https://access.redhat.com/errata/RHSA-2026:27742
- https://access.redhat.com/errata/RHSA-2026:27743
- https://access.redhat.com/errata/RHSA-2026:28037
- https://access.redhat.com/errata/RHSA-2026:28143
- https://access.redhat.com/errata/RHSA-2026:28999
- https://access.redhat.com/errata/RHSA-2026:29212
- https://access.redhat.com/errata/RHSA-2026:29815
- https://access.redhat.com/errata/RHSA-2026:29904
