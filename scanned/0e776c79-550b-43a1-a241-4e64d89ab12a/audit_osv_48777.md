# [M] CVE-2018-13093

## Summary
Severity: Medium
Advisory: CVE-2018-13093
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13093
Type: osv

## Details
An issue was discovered in fs/xfs/xfs_icache.c in the Linux kernel through 4.17.3. There is a NULL pointer dereference and panic in lookup_slow() on a NULL inode->i_ops pointer when doing pathwalks on a corrupted xfs image. This occurs because of a lack of proper validation that cached inodes are free during allocation.

## References
- https://usn.ubuntu.com/4118-1/
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4094-1/
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://bugzilla.kernel.org/show_bug.cgi?id=199367
- https://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git/commit/?h=for-next&id=afca6c5b2595fc44383919fba740c194b0b76aff
- https://github.com/torvalds/linux/commit/afca6c5b2595fc44383919fba740c194b0b76aff
