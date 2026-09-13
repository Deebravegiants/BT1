# [H] In rsync 3.0.1 through 3.4.1, `receive_xattr` relies on an untrusted length value during a qsort...

## Summary
Severity: High
Advisory: JLSEC-2026-627
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/JLSEC-2026-627
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.4+0

## Details
In rsync 3.0.1 through 3.4.1, `receive_xattr` relies on an untrusted length value during a qsort call, leading to a receiver use-after-free. The victim must run rsync with -X (aka --xattrs). On Linux, many (but not all) common configurations are vulnerable. Non-Linux platforms are more widely vulnerable.

## References
- http://www.openwall.com/lists/oss-security/2026/04/16/9
- http://www.openwall.com/lists/oss-security/2026/04/22/3
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
- https://access.redhat.com/errata/RHSA-2026:25190
- https://access.redhat.com/errata/RHSA-2026:26542
