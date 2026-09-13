# [M] CVE-2019-15217

## Summary
Severity: Medium
Advisory: CVE-2019-15217
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15217
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2.3. There is a NULL pointer dereference caused by a malicious USB device in the drivers/media/usb/zr364xx/zr364xx.c driver.

## References
- http://www.openwall.com/lists/oss-security/2019/08/22/4
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4286-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://www.openwall.com/lists/oss-security/2019/08/22/3
- http://www.openwall.com/lists/oss-security/2019/08/22/5
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4302-1/
- http://www.openwall.com/lists/oss-security/2019/08/22/2
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4147-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5d2e73a5f80a5b5aff3caf1ec6d39b5b3f54b26e
- https://syzkaller.appspot.com/bug?id=9c0c178c24d828a7378f483309001329750aad64
