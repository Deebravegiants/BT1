# [M] CVE-2019-19531

## Summary
Severity: Medium
Advisory: CVE-2019-19531
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19531
Type: osv

## Details
In the Linux kernel before 5.2.9, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/usb/misc/yurex.c driver, aka CID-fc05481b2fca.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.9
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fc05481b2fcabaaeccf63e32ac1baab54e5b6963
