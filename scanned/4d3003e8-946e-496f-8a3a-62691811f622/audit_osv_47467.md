# [M] CVE-2016-6130

## Summary
Severity: Medium
Advisory: CVE-2016-6130
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-07-03
Source: https://osv.dev/vulnerability/CVE-2016-6130
Type: osv

## Details
Race condition in the sclp_ctl_ioctl_sccb function in drivers/s390/char/sclp_ctl.c in the Linux kernel before 4.6 allows local users to obtain sensitive information from kernel memory by changing a certain length value, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/bid/91540
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=532c34b5fbf1687df63b3fcd5b2846312ac943c6
- http://www.securityfocus.com/archive/1/538803/30/0/threaded
- http://www.debian.org/security/2016/dsa-3616
- https://bugzilla.kernel.org/show_bug.cgi?id=116741
- https://github.com/torvalds/linux/commit/532c34b5fbf1687df63b3fcd5b2846312ac943c6
