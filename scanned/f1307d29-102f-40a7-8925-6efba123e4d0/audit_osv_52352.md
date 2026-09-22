# [M] CVE-2021-47359

## Summary
Severity: Medium
Advisory: CVE-2021-47359
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47359
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix soft lockup during fsstress

Below traces are observed during fsstress and system got hung.
[  130.698396] watchdog: BUG: soft lockup - CPU#6 stuck for 26s!

## References
- https://git.kernel.org/stable/c/71826b068884050d5fdd37fda857ba1539c513d3
- https://git.kernel.org/stable/c/9f6c7aff21f81ae8856da1f63847d1362d523409
