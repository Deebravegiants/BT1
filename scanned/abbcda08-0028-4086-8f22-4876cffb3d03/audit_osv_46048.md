# [M] JLSEC-2026-605

## Summary
Severity: Medium
Advisory: JLSEC-2026-605
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-605
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Covert timing channel in comparison of MD5-hashed password in PostgreSQL authentication allows an attacker to recover user credentials sufficient to authenticate.  This does not affect scram-sha-256 passwords, the default in all supported releases.  However, current databases may have MD5-hashed passwords originating in upgrades from PostgreSQL 13 or earlier.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
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
- https://access.redhat.com/errata/RHSA-2026:29815
- https://access.redhat.com/errata/RHSA-2026:29904
