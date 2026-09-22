# [H] CVE-2020-11668

## Summary
Severity: High
Advisory: CVE-2020-11668
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-04-09
Source: https://osv.dev/vulnerability/CVE-2020-11668
Type: osv

## Details
In the Linux kernel before 5.6.1, drivers/media/usb/gspca/xirlink_cit.c (aka the Xirlink camera USB driver) mishandles invalid descriptors, aka CID-a246b4d54770.

## References
- https://usn.ubuntu.com/4369-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4345-1/
- https://usn.ubuntu.com/4364-1/
- https://usn.ubuntu.com/4368-1/
- https://www.debian.org/security/2020/dsa-4698
- https://security.netapp.com/advisory/ntap-20200430-0004/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.1
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a246b4d547708f33ff4d4b9a7a5dbac741dc89d8
- https://github.com/torvalds/linux/commit/a246b4d547708f33ff4d4b9a7a5dbac741dc89d8
