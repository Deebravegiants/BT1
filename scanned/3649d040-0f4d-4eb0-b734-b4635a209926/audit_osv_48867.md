# [M] CVE-2018-16658

## Summary
Severity: Medium
Advisory: CVE-2018-16658
CVSS: 6.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2018-09-07
Source: https://osv.dev/vulnerability/CVE-2018-16658
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.18.6. An information leak in cdrom_ioctl_drive_status in drivers/cdrom/cdrom.c could be used by local attackers to read kernel memory because a cast from unsigned long to int interferes with bounds checking. This is similar to CVE-2018-10940.

## References
- https://usn.ubuntu.com/3797-1/
- https://usn.ubuntu.com/3797-2/
- https://usn.ubuntu.com/3820-1/
- https://usn.ubuntu.com/3822-1/
- https://usn.ubuntu.com/3822-2/
- https://www.debian.org/security/2018/dsa-4308
- http://www.securityfocus.com/bid/105334
- https://access.redhat.com/errata/RHSA-2019:4154
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.6
- https://usn.ubuntu.com/3820-3/
- https://usn.ubuntu.com/3820-2/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8f3fafc9c2f0ece10832c25f7ffcb07c97a32ad4
- https://github.com/torvalds/linux/commit/8f3fafc9c2f0ece10832c25f7ffcb07c97a32ad4
