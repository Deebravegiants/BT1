# [M] CVE-2017-14156

## Summary
Severity: Medium
Advisory: CVE-2017-14156
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-14156
Type: osv

## Details
The atyfb_ioctl function in drivers/video/fbdev/aty/atyfb_base.c in the Linux kernel through 4.12.10 does not initialize a certain data structure, which allows local users to obtain sensitive information from kernel stack memory by reading locations associated with padding bytes.

## References
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- http://www.securityfocus.com/bid/100634
- http://www.debian.org/security/2017/dsa-3981
- https://marc.info/?l=linux-kernel&m=150453196710422&w=2
- https://github.com/torvalds/linux/pull/441
- https://marc.info/?l=linux-kernel&m=150401461613306&w=2
