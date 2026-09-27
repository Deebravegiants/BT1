# [M] CVE-2019-19530

## Summary
Severity: Medium
Advisory: CVE-2019-19530
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19530
Type: osv

## Details
In the Linux kernel before 5.2.10, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/usb/class/cdc-acm.c driver, aka CID-c52873e5a1ef.

## References
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c52873e5a1ef72f845526d9f6a50704433f9c625
