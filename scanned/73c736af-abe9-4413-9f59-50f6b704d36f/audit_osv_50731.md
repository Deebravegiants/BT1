# [M] CVE-2020-36322

## Summary
Severity: Medium
Advisory: CVE-2020-36322
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2020-36322
Type: osv

## Details
An issue was discovered in the FUSE filesystem implementation in the Linux kernel before 5.10.6, aka CID-5d069dbe8aaf. fuse_do_getattr() calls make_bad_inode() in inappropriate situations, causing a system crash. NOTE: the original fix for this vulnerability was incomplete, and its incompleteness is tracked as CVE-2021-28950.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.6
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5096
- https://www.starwindsoftware.com/security/sw-20220816-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5d069dbe8aaf2a197142558b6fb2978189ba3454
