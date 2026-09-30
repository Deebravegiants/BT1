# [M] CVE-2019-15218

## Summary
Severity: Medium
Advisory: CVE-2019-15218
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15218
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.1.8. There is a NULL pointer dereference caused by a malicious USB device in the drivers/media/usb/siano/smsusb.c driver.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.8
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/08/22/4
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4147-1/
- http://www.openwall.com/lists/oss-security/2019/08/22/2
- http://www.openwall.com/lists/oss-security/2019/08/22/3
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=31e0456de5be379b10fea0fa94a681057114a96e
- http://www.openwall.com/lists/oss-security/2019/08/22/5
- https://syzkaller.appspot.com/bug?id=4a5d7c8c2b6dbedb5b7218c6d7e8666bd2387517
