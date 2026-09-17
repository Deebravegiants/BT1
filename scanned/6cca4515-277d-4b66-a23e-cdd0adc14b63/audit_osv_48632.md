# [M] CVE-2018-10323

## Summary
Severity: Medium
Advisory: CVE-2018-10323
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2018-10323
Type: osv

## Details
The xfs_bmap_extents_to_btree function in fs/xfs/libxfs/xfs_bmap.c in the Linux kernel through 4.16.3 allows local users to cause a denial of service (xfs_bmapi_write NULL pointer dereference) via a crafted xfs image.

## References
- https://usn.ubuntu.com/4486-1/
- https://usn.ubuntu.com/3752-3/
- https://www.debian.org/security/2018/dsa-4188
- http://www.securityfocus.com/bid/103959
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3754-1/
- https://usn.ubuntu.com/3752-1/
- https://bugzilla.kernel.org/show_bug.cgi?id=199423
- https://www.spinics.net/lists/linux-xfs/msg17254.html
