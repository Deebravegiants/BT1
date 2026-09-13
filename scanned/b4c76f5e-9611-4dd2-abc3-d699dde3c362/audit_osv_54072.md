# [H] CVE-2023-3812

## Summary
Severity: High
Advisory: CVE-2023-3812
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3812
Type: osv

## Details
An out-of-bounds memory access flaw was found in the Linux kernel’s TUN/TAP device driver functionality in how a user generates a malicious (too big) networking packet when napi frags is enabled. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://access.redhat.com/errata/RHSA-2023:7370
- https://access.redhat.com/errata/RHSA-2023:7382
- https://access.redhat.com/errata/RHSA-2023:7418
- https://access.redhat.com/errata/RHSA-2023:7549
- https://access.redhat.com/errata/RHSA-2024:0340
- https://access.redhat.com/errata/RHSA-2024:0378
- https://access.redhat.com/errata/RHSA-2024:2008
- https://access.redhat.com/errata/RHSA-2023:6813
- https://access.redhat.com/errata/RHSA-2023:7389
- https://access.redhat.com/errata/RHSA-2023:7548
- https://access.redhat.com/errata/RHSA-2024:0461
- https://access.redhat.com/errata/RHSA-2024:0562
- https://access.redhat.com/errata/RHSA-2024:0563
- https://access.redhat.com/errata/RHSA-2024:0575
- https://access.redhat.com/errata/RHSA-2024:1961
- https://access.redhat.com/errata/RHSA-2023:6799
- https://access.redhat.com/errata/RHSA-2023:7554
- https://access.redhat.com/errata/RHSA-2024:0554
- https://access.redhat.com/errata/RHSA-2024:0593
- https://access.redhat.com/security/cve/CVE-2023-3812
