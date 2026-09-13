# [M] CVE-2019-15211

## Summary
Severity: Medium
Advisory: CVE-2019-15211
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15211
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2.6. There is a use-after-free caused by a malicious USB device in the drivers/media/v4l2-core/v4l2-dev.c driver because drivers/media/radio/radio-raremono.c does not properly allocate memory.

## References
- https://usn.ubuntu.com/4145-1/
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.6
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4147-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c666355e60ddb4748ead3bdd983e3f7f2224aaf0
- https://syzkaller.appspot.com/bug?id=775f90f43cfd6f8ac6c15251ce68e604453da226
