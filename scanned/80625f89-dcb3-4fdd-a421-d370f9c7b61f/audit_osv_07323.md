# [H] Postgresql: buffer overrun from integer overflow in array modification

## Summary
Severity: High
Advisory: BIT-postgresql-2023-5869
Aliases: CVE-2023-5869
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2023-5869
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=16.0.0 <16.0.1

## Details
A flaw was found in PostgreSQL that allows authenticated database users to execute arbitrary code through missing overflow checks during SQL array value modification. This issue exists due to an integer overflow during array modification where a remote user can trigger the overflow by providing specially crafted data. This enables the execution of arbitrary code on the target system, allowing users to write arbitrary bytes to memory and extensively read the server's memory.

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
- https://access.redhat.com/errata/RHSA-2023:7771
- https://access.redhat.com/errata/RHSA-2023:7772
- https://access.redhat.com/errata/RHSA-2023:7778
- https://access.redhat.com/errata/RHSA-2023:7783
- https://access.redhat.com/errata/RHSA-2023:7784
- https://access.redhat.com/errata/RHSA-2023:7785
- https://access.redhat.com/errata/RHSA-2023:7786
- https://access.redhat.com/errata/RHSA-2023:7788
