# [H] CVE-2016-10044

## Summary
Severity: High
Advisory: CVE-2016-10044
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2016-10044
Type: osv

## Details
The aio_mount function in fs/aio.c in the Linux kernel before 4.7.7 does not properly restrict execute access, which makes it easier for local users to bypass intended SELinux W^X policy restrictions, and consequently gain privileges, via an io_setup system call.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.7
- http://www.securityfocus.com/bid/96122
- http://www.securitytracker.com/id/1037798
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=22f6b4d34fcf039c63a94e7670e0da24f8575a5a
- http://source.android.com/security/bulletin/2017-02-01.html
- https://github.com/torvalds/linux/commit/22f6b4d34fcf039c63a94e7670e0da24f8575a5a
