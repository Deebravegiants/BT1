# [M] CVE-2019-19537

## Summary
Severity: Medium
Advisory: CVE-2019-19537
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19537
Type: osv

## Details
In the Linux kernel before 5.2.10, there is a race condition bug that can be caused by a malicious USB device in the USB character device driver layer, aka CID-303911cfc5b9. This affects drivers/usb/core/file.c.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=303911cfc5b95d33687d9046133ff184cf5043ff
