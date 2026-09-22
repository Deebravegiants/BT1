# [M] CVE-2018-10322

## Summary
Severity: Medium
Advisory: CVE-2018-10322
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2018-10322
Type: osv

## Details
The xfs_dinode_verify function in fs/xfs/libxfs/xfs_inode_buf.c in the Linux kernel through 4.16.3 allows local users to cause a denial of service (xfs_ilock_attr_map_shared invalid pointer dereference) via a crafted xfs image.

## References
- https://usn.ubuntu.com/4578-1/
- https://usn.ubuntu.com/4579-1/
- https://access.redhat.com/errata/RHSA-2018:3096
- http://www.securityfocus.com/bid/103960
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://bugzilla.kernel.org/show_bug.cgi?id=199377
- https://www.spinics.net/lists/linux-xfs/msg17215.html
