# [M] CVE-2019-19525

## Summary
Severity: Medium
Advisory: CVE-2019-19525
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19525
Type: osv

## Details
In the Linux kernel before 5.3.6, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/net/ieee802154/atusb.c driver, aka CID-7fd25e6fc035.

## References
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.6
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7fd25e6fc035f4b04b75bca6d7e8daa069603a76
