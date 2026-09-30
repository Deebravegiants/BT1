# [M] CVE-2018-13095

## Summary
Severity: Medium
Advisory: CVE-2018-13095
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13095
Type: osv

## Details
An issue was discovered in fs/xfs/libxfs/xfs_inode_buf.c in the Linux kernel through 4.17.3. A denial of service (memory corruption and BUG) can occur for a corrupted xfs image upon encountering an inode that is in extent format, but has more extents than fit in the inode fork.

## References
- https://access.redhat.com/errata/RHSA-2019:1350
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://bugzilla.kernel.org/show_bug.cgi?id=199915
- https://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git/commit/?h=for-next&id=23fcb3340d033d9f081e21e6c12c2db7eaa541d3
- https://github.com/torvalds/linux/commit/23fcb3340d033d9f081e21e6c12c2db7eaa541d3
