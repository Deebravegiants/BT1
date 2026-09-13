# [M] CVE-2019-15212

## Summary
Severity: Medium
Advisory: CVE-2019-15212
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15212
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.1.8. There is a double-free caused by a malicious USB device in the drivers/usb/misc/rio500.c driver.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.8
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4147-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3864d33943b4a76c6e64616280e98d2410b1190f
- https://syzkaller.appspot.com/bug?id=64aa96c96f594a77eb8d945df21ec76dd35573b3
