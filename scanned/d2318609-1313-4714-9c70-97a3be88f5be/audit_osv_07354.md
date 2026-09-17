# [H] PostgreSQL intarray missing validation of type of input to selectivity estimator executes arbitrary code

## Summary
Severity: High
Advisory: BIT-postgresql-2026-2004
Aliases: CVE-2026-2004
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-2004
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.2.0

## Details
Missing validation of type of input in PostgreSQL intarray extension selectivity estimator function allows an object creator to execute arbitrary code as the operating system user running the database.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2004
- https://www.postgresql.org/support/security/CVE-2026-2004/
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
