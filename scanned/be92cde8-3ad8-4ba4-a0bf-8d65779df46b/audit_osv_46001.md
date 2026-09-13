# [H] JLSEC-2026-56

## Summary
Severity: High
Advisory: JLSEC-2026-56
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-56
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=14.1.0+0 <16.13.0+0

## Details
Missing validation of multibyte character length in PostgreSQL text manipulation allows a database user to issue crafted queries that achieve a buffer overrun.  That suffices to execute arbitrary code as the operating system user running the database.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://access.redhat.com/errata/RHSA-2026:19009
- https://access.redhat.com/errata/RHSA-2026:19010
- https://access.redhat.com/errata/RHSA-2026:3730
- https://access.redhat.com/errata/RHSA-2026:3887
- https://access.redhat.com/errata/RHSA-2026:3896
- https://access.redhat.com/errata/RHSA-2026:4024
- https://access.redhat.com/errata/RHSA-2026:4059
- https://access.redhat.com/errata/RHSA-2026:4063
- https://access.redhat.com/errata/RHSA-2026:4064
- https://access.redhat.com/errata/RHSA-2026:4074
- https://access.redhat.com/errata/RHSA-2026:4075
- https://access.redhat.com/errata/RHSA-2026:4110
- https://access.redhat.com/errata/RHSA-2026:4254
- https://access.redhat.com/errata/RHSA-2026:4441
- https://access.redhat.com/errata/RHSA-2026:4475
- https://access.redhat.com/errata/RHSA-2026:4504
- https://access.redhat.com/errata/RHSA-2026:4505
- https://access.redhat.com/errata/RHSA-2026:4506
- https://access.redhat.com/errata/RHSA-2026:4509
- https://access.redhat.com/errata/RHSA-2026:4515
