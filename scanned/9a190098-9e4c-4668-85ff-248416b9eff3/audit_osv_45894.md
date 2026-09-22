# [M] JLSEC-2026-45

## Summary
Severity: Medium
Advisory: JLSEC-2026-45
Ecosystem: Julia
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-45
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.8.0+0

## Details
A flaw was found in PostgreSQL involving the `pg_cancel_backend` role that signals background workers, including the logical replication launcher, autovacuum workers, and the autovacuum launcher. Successful exploitation requires a non-core extension with a less-resilient background worker and would affect that specific background worker only. This issue may allow a remote high privileged user to launch a denial of service (DoS) attack.

## References
- https://access.redhat.com/errata/RHSA-2023:7545
- https://access.redhat.com/errata/RHSA-2023:7579
- https://access.redhat.com/errata/RHSA-2023:7580
- https://access.redhat.com/errata/RHSA-2023:7581
- https://access.redhat.com/errata/RHSA-2023:7616
- https://access.redhat.com/errata/RHSA-2023:7656
- https://access.redhat.com/errata/RHSA-2023:7666
- https://access.redhat.com/errata/RHSA-2023:7667
- https://access.redhat.com/errata/RHSA-2023:7694
- https://access.redhat.com/errata/RHSA-2023:7695
- https://access.redhat.com/errata/RHSA-2023:7714
- https://access.redhat.com/errata/RHSA-2023:7770
- https://access.redhat.com/errata/RHSA-2023:7772
- https://access.redhat.com/errata/RHSA-2023:7784
- https://access.redhat.com/errata/RHSA-2023:7785
- https://access.redhat.com/errata/RHSA-2023:7883
- https://access.redhat.com/errata/RHSA-2023:7884
- https://access.redhat.com/errata/RHSA-2023:7885
- https://access.redhat.com/errata/RHSA-2024:0304
- https://access.redhat.com/errata/RHSA-2024:0332
