# [H] PostgreSQL missing validation of multibyte character length executes arbitrary code

## Summary
Severity: High
Advisory: BIT-postgresql-2026-2006
Aliases: CVE-2026-2006
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-2006
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.2.0

## Details
Missing validation of multibyte character length in PostgreSQL text manipulation allows a database user to issue crafted queries that achieve a buffer overrun.  That suffices to execute arbitrary code as the operating system user running the database.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2006
- https://www.postgresql.org/support/security/CVE-2026-2006/
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
