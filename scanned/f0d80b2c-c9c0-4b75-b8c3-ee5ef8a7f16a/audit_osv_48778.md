# [M] CVE-2018-13094

## Summary
Severity: Medium
Advisory: CVE-2018-13094
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13094
Type: osv

## Details
An issue was discovered in fs/xfs/libxfs/xfs_attr_leaf.c in the Linux kernel through 4.17.3. An OOPS may occur for a corrupted xfs image after xfs_da_shrink_inode() is called with a NULL bp.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://access.redhat.com/errata/RHSA-2019:0831
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3752-3/
- https://usn.ubuntu.com/3753-2/
- https://usn.ubuntu.com/3754-1/
- https://bugzilla.kernel.org/show_bug.cgi?id=199969
- https://github.com/torvalds/linux/commit/bb3d48dcf86a97dc25fe9fc2c11938e19cb4399a
- https://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git/commit/?h=for-next&id=bb3d48dcf86a97dc25fe9fc2c11938e19cb4399a
