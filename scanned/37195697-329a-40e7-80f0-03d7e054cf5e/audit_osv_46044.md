# [H] JLSEC-2026-601

## Summary
Severity: High
Advisory: JLSEC-2026-601
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-601
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Integer wraparound in multiple PostgreSQL server features allows an unprivileged database user to cause the server to undersize an allocation and write out-of-bounds.  This may execute arbitrary code as the operating system user running the database.  In applications that pass gigabyte-scale user inputs to the relevant database functions, the application input provider may achieve a segmentation fault.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
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
- https://access.redhat.com/errata/RHSA-2026:28208
- https://access.redhat.com/errata/RHSA-2026:28999
- https://access.redhat.com/errata/RHSA-2026:29212
- https://access.redhat.com/errata/RHSA-2026:29815
- https://access.redhat.com/errata/RHSA-2026:29904
- https://access.redhat.com/errata/RHSA-2026:29953
