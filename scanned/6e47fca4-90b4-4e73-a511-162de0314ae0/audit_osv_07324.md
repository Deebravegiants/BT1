# [M] Postgresql: role pg_signal_backend can signal certain superuser processes.

## Summary
Severity: Medium
Advisory: BIT-postgresql-2023-5870
Aliases: CVE-2023-5870
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2023-5870
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=16.0.0 <16.0.1

## Details
A flaw was found in PostgreSQL involving the pg_cancel_backend role that signals background workers, including the logical replication launcher, autovacuum workers, and the autovacuum launcher. Successful exploitation requires a non-core extension with a less-resilient background worker and would affect that specific background worker only. This issue may allow a remote high privileged user to launch a denial of service (DoS) attack.

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
