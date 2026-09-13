# [H] CVE-2020-29661

## Summary
Severity: High
Advisory: CVE-2020-29661
Aliases: A-175451802, ASB-A-175451802
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-29661
Type: osv

## Details
A locking issue was discovered in the tty subsystem of the Linux kernel through 5.9.13. drivers/tty/tty_jobctrl.c allows a use-after-free attack against TIOCSPGRP, aka CID-54ffccbf053b.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZ7OAKAEFAXQRGBZK4LYUWINCD3D2XCL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BOB25SU6XUL4TNP7KB63WNZSYTIYFDPP/
- http://packetstormsecurity.com/files/164950/Kernel-Live-Patch-Security-Notice-LSN-0082-1.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://security.netapp.com/advisory/ntap-20210122-0001/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://www.debian.org/security/2021/dsa-4843
- http://packetstormsecurity.com/files/160681/Linux-TIOCSPGRP-Broken-Locking.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=54ffccbf053b5b6ca4f6e45094b942fab92a25fc
- http://www.openwall.com/lists/oss-security/2020/12/10/1
- https://www.oracle.com/security-alerts/cpuoct2021.html
