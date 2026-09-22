# [M] CVE-2019-19535

## Summary
Severity: Medium
Advisory: CVE-2019-19535
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19535
Type: osv

## Details
In the Linux kernel before 5.2.9, there is an info-leak bug that can be caused by a malicious USB device in the drivers/net/can/usb/peak_usb/pcan_usb_fd.c driver, aka CID-30a8beeb3042.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.9
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=30a8beeb3042f49d0537b7050fd21b490166a3d9
