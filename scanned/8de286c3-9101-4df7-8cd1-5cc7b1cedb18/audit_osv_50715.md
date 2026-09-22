# [M] CVE-2020-29660

## Summary
Severity: Medium
Advisory: CVE-2020-29660
Aliases: A-175451844, ASB-A-175451844
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-29660
Type: osv

## Details
A locking inconsistency issue was discovered in the tty subsystem of the Linux kernel through 5.9.13. drivers/tty/tty_io.c and drivers/tty/tty_jobctrl.c may allow a read-after-free attack against TIOCGSID, aka CID-c8bcd9c5be24.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BOB25SU6XUL4TNP7KB63WNZSYTIYFDPP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZ7OAKAEFAXQRGBZK4LYUWINCD3D2XCL/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://security.netapp.com/advisory/ntap-20210122-0001/
- https://www.debian.org/security/2021/dsa-4843
- http://www.openwall.com/lists/oss-security/2020/12/10/1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c8bcd9c5be24fb9e6132e97da5a35e55a83e36b9
- http://packetstormsecurity.com/files/164950/Kernel-Live-Patch-Security-Notice-LSN-0082-1.html
