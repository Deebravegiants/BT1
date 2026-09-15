# [M] CVE-2019-15215

## Summary
Severity: Medium
Advisory: CVE-2019-15215
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15215
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2.6. There is a use-after-free caused by a malicious USB device in the drivers/media/usb/cpia2/cpia2_usb.c driver.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://usn.ubuntu.com/4115-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.6
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4145-1/
- https://usn.ubuntu.com/4147-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=eff73de2b1600ad8230692f00bc0ab49b166512a
- https://syzkaller.appspot.com/bug?id=b68d3c254cf294f8a802582094fa3251d6de5247
