# [M] CVE-2019-19527

## Summary
Severity: Medium
Advisory: CVE-2019-19527
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19527
Type: osv

## Details
In the Linux kernel before 5.2.10, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/hid/usbhid/hiddev.c driver, aka CID-9c09b214f30e.

## References
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6d4472d7bec39917b54e4e80245784ea5d60ce49
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9c09b214f30e3c11f9b0b03f89442df03643794d
