# [M] CVE-2020-12655

## Summary
Severity: Medium
Advisory: CVE-2020-12655
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-12655
Type: osv

## Details
An issue was discovered in xfs_agf_verify in fs/xfs/libxfs/xfs_alloc.c in the Linux kernel through 5.6.10. Attackers may trigger a sync of excessive duration via an XFS v5 image with crafted metadata, aka CID-d0c7feaf8767.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IZ2X3TM6RGRUS3KZAS26IJO5XGU7TBBR/
- https://usn.ubuntu.com/4465-1/
- https://usn.ubuntu.com/4483-1/
- https://usn.ubuntu.com/4485-1/
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ES5C6ZCMALBEBMKNNCTBSLLSYGFZG3FF/
- https://lore.kernel.org/linux-xfs/20200221153803.GP9506%40magnolia/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IO5XIQSRI747P4RVVTNX7TUPEOCF4OPU/
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://github.com/torvalds/linux/commit/d0c7feaf87678371c2c09b3709400be416b2dc62
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d0c7feaf87678371c2c09b3709400be416b2dc62
