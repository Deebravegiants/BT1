# [M] CVE-2021-28950

## Summary
Severity: Medium
Advisory: CVE-2021-28950
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-20
Source: https://osv.dev/vulnerability/CVE-2021-28950
Type: osv

## Details
An issue was discovered in fs/fuse/fuse_i.h in the Linux kernel before 5.11.8. A "stall on CPU" can occur because a retry loop continually finds the same bad inode, aka CID-775c5033a0d1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FB6LUXPEIRLZH32YXWZVEZAD4ZL6SDK2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QRTPQE73ANG7D6M4L4PK5ZQDPO4Y2FVD/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5096
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.8
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=775c5033a0d164622d9d10dd0f0a5531639ed3ed
