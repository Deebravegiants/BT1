# [M] JLSEC-2026-43

## Summary
Severity: Medium
Advisory: JLSEC-2026-43
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-43
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.8.0+0

## Details
A memory disclosure vulnerability was found in PostgreSQL that allows remote users to access sensitive information by exploiting certain aggregate function calls with 'unknown'-type arguments. Handling 'unknown'-type values from string literals without type designation can disclose bytes, potentially revealing notable and confidential information. This issue exists due to excessive data output in aggregate function calls, enabling remote users to read some portion of system memory.

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
