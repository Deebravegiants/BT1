# [M] CVE-2019-15216

## Summary
Severity: Medium
Advisory: CVE-2019-15216
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15216
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.14. There is a NULL pointer dereference caused by a malicious USB device in the drivers/usb/misc/yurex.c driver.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- http://www.openwall.com/lists/oss-security/2019/08/22/3
- http://www.openwall.com/lists/oss-security/2019/08/22/2
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://usn.ubuntu.com/4118-1/
- http://www.openwall.com/lists/oss-security/2019/08/22/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.14
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- http://www.openwall.com/lists/oss-security/2019/08/22/5
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4115-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ef61eb43ada6c1d6b94668f0f514e4c268093ff3
- https://syzkaller.appspot.com/bug?id=f0b1f2952022c75394c0eef2afeb17af90f9227e
