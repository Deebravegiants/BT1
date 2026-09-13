# [M] CVE-2023-4133

## Summary
Severity: Medium
Advisory: CVE-2023-4133
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-03
Source: https://osv.dev/vulnerability/CVE-2023-4133
Type: osv

## Details
A use-after-free vulnerability was found in the cxgb4 driver in the Linux kernel. The bug occurs when the cxgb4 device is detaching due to a possible rearming of the flower_stats_timer from the work queue. This flaw allows a local user to crash the system, causing a denial of service condition.

## References
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-4133
- https://access.redhat.com/errata/RHSA-2024:2394
- https://bugzilla.redhat.com/show_bug.cgi?id=2221702
