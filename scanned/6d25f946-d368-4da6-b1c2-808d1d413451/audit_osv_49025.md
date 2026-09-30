# [M] CVE-2018-20511

## Summary
Severity: Medium
Advisory: CVE-2018-20511
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-27
Source: https://osv.dev/vulnerability/CVE-2018-20511
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.18.11. The ipddp_ioctl function in drivers/net/appletalk/ipddp.c allows local users to obtain sensitive kernel address information by leveraging CAP_NET_ADMIN to read the ipddp_route dev and next fields via an SIOCFINDIPDDPRT ioctl call.

## References
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4094-1/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.11
- http://www.securityfocus.com/bid/106347
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lkml.org/lkml/2018/9/27/480
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9824dfae5741275473a23a7ed5756c7b6efacc9d
- https://github.com/torvalds/linux/commit/9824dfae5741275473a23a7ed5756c7b6efacc9d
