# [M] CVE-2019-15291

## Summary
Severity: Medium
Advisory: CVE-2019-15291
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-20
Source: https://osv.dev/vulnerability/CVE-2019-15291
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.2.9. There is a NULL pointer dereference caused by a malicious USB device in the flexcop_usb_probe function in the drivers/media/usb/b2c2/flexcop-usb.c driver.

## References
- https://usn.ubuntu.com/4258-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4254-2/
- https://usn.ubuntu.com/4284-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00036.html
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://usn.ubuntu.com/4254-1/
- https://usn.ubuntu.com/4287-2/
- https://seclists.org/bugtraq/2020/Jan/10
- https://usn.ubuntu.com/4287-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00037.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- http://www.openwall.com/lists/oss-security/2019/08/22/1
- https://syzkaller.appspot.com/bug?id=c0203bd72037d07493f4b7562411e4f5f4553a8f
