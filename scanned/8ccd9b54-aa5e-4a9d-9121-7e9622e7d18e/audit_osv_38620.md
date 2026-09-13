# [H] CVE-2026-41035

## Summary
Severity: High
Advisory: CVE-2026-41035
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-41035
Type: osv

## Details
In rsync 3.0.1 through 3.4.1, receive_xattr relies on an untrusted length value during a qsort call, leading to a receiver use-after-free. The victim must run rsync with -X (aka --xattrs). On Linux, many (but not all) common configurations are vulnerable. Non-Linux platforms are more widely vulnerable.

## References
- http://www.openwall.com/lists/oss-security/2026/04/16/9
- http://www.openwall.com/lists/oss-security/2026/04/22/3
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41035.json
- https://www.openwall.com/lists/oss-security/2026/04/16/2
- https://access.redhat.com/errata/RHSA-2026:17481
- https://access.redhat.com/errata/RHSA-2026:19152
- https://access.redhat.com/errata/RHSA-2026:19368
- https://access.redhat.com/errata/RHSA-2026:20601
- https://access.redhat.com/errata/RHSA-2026:20602
- https://access.redhat.com/errata/RHSA-2026:20603
- https://access.redhat.com/errata/RHSA-2026:20604
- https://access.redhat.com/errata/RHSA-2026:20696
- https://access.redhat.com/errata/RHSA-2026:23233
- https://access.redhat.com/errata/RHSA-2026:23245
- https://access.redhat.com/errata/RHSA-2026:25044
- https://access.redhat.com/errata/RHSA-2026:25149
- https://access.redhat.com/errata/RHSA-2026:25170
- https://access.redhat.com/errata/RHSA-2026:25172
- https://access.redhat.com/errata/RHSA-2026:25173
- https://access.redhat.com/errata/RHSA-2026:25181
