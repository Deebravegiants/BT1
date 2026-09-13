# [M] CVE-2017-6348

## Summary
Severity: Medium
Advisory: CVE-2017-6348
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-6348
Type: osv

## Details
The hashbin_delete function in net/irda/irqueue.c in the Linux kernel before 4.9.13 improperly manages lock dropping, which allows local users to cause a denial of service (deadlock) via crafted operations on IrDA devices.

## References
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/96483
- http://www.debian.org/security/2017/dsa-3804
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4c03b862b12f980456f9de92db6d508a4999b788
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.13
- http://www.openwall.com/lists/oss-security/2017/02/28/4
- https://github.com/torvalds/linux/commit/4c03b862b12f980456f9de92db6d508a4999b788
