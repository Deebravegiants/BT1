# [M] CVE-2020-11608

## Summary
Severity: Medium
Advisory: CVE-2020-11608
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-07
Source: https://osv.dev/vulnerability/CVE-2020-11608
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.6.1. drivers/media/usb/gspca/ov519.c allows NULL pointer dereferences in ov511_mode_init_regs and ov518_mode_init_regs when there are zero endpoints, aka CID-998912346c0d.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://usn.ubuntu.com/4369-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4364-1/
- https://usn.ubuntu.com/4368-1/
- https://www.debian.org/security/2020/dsa-4698
- https://security.netapp.com/advisory/ntap-20200430-0004/
- https://usn.ubuntu.com/4345-1/
- https://github.com/torvalds/linux/commit/998912346c0da53a6dbb71fab3a138586b596b30
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.1
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=998912346c0da53a6dbb71fab3a138586b596b30
