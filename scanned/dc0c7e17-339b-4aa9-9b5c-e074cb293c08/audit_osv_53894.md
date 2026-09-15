# [M] CVE-2023-31085

## Summary
Severity: Medium
Advisory: CVE-2023-31085
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-31085
Type: osv

## Details
An issue was discovered in drivers/mtd/ubi/cdev.c in the Linux kernel 6.2. There is a divide-by-zero error in do_div(sz,mtd->erasesize), used indirectly by ctrl_cdev_ioctl, when mtd->erasesize is 0.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=017c73a34a661a861712f7cc1393a123e5b2208c
- https://lore.kernel.org/all/687864524.118195.1681799447034.JavaMail.zimbra%40nod.at/
- https://security.netapp.com/advisory/ntap-20230929-0003/
