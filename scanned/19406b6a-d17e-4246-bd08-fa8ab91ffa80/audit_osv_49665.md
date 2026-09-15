# [M] CVE-2019-15221

## Summary
Severity: Medium
Advisory: CVE-2019-15221
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15221
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.1.17. There is a NULL pointer dereference caused by a malicious USB device in the sound/usb/line6/pcm.c driver.

## References
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4286-2/
- https://usn.ubuntu.com/4147-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.17
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3450121997ce872eb7f1248417225827ea249710
- https://syzkaller.appspot.com/bug?id=240f09164db2c3d3af33a117c713dc7650dc29d6
