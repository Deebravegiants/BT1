# [M] CVE-2018-14612

## Summary
Severity: Medium
Advisory: CVE-2018-14612
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-14612
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.10. There is an invalid pointer dereference in btrfs_root_node() when mounting a crafted btrfs image, because of a lack of chunk block group mapping validation in btrfs_read_block_groups in fs/btrfs/extent-tree.c, and a lack of empty-tree checks in check_leaf in fs/btrfs/tree-checker.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- http://www.securityfocus.com/bid/104917
- https://bugzilla.kernel.org/show_bug.cgi?id=199847
- https://patchwork.kernel.org/patch/10503403/
- https://patchwork.kernel.org/patch/10503413/
