# [M] CVE-2019-19536

## Summary
Severity: Medium
Advisory: CVE-2019-19536
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19536
Type: osv

## Details
In the Linux kernel before 5.2.9, there is an info-leak bug that can be caused by a malicious USB device in the drivers/net/can/usb/peak_usb/pcan_usb_pro.c driver, aka CID-ead16e53c2f0.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ead16e53c2f0ed946d82d4037c630e2f60f4ab69
