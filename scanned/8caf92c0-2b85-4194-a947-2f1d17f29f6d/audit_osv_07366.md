# [H] PostgreSQL discloses MD5-hashed passwords via covert timing channel

## Summary
Severity: High
Advisory: BIT-postgresql-2026-6478
Aliases: CVE-2026-6478
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-6478
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.4.0

## Details
Covert timing channel in comparison of MD5-hashed password in PostgreSQL authentication allows an attacker to recover user credentials sufficient to authenticate.  This does not affect scram-sha-256 passwords, the default in all supported releases.  However, current databases may have MD5-hashed passwords originating in upgrades from PostgreSQL 13 or earlier.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6478
- https://www.postgresql.org/support/security/CVE-2026-6478/
- https://access.redhat.com/errata/RHSA-2026:21182
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
