# [M] CVE-2021-4149

## Summary
Severity: Medium
Advisory: CVE-2021-4149
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-4149
Type: osv

## Details
A vulnerability was found in btrfs_alloc_tree_b in fs/btrfs/extent-tree.c in the Linux kernel due to an improper lock operation in btrfs. In this flaw, a user with a local privilege may cause a denial of service (DOS) due to a deadlock problem.

## References
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2026485
- https://lkml.org/lkml/2021/10/18/885
- https://lkml.org/lkml/2021/9/13/2565
