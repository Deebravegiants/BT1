# [M] CVE-2019-19523

## Summary
Severity: Medium
Advisory: CVE-2019-19523
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19523
Type: osv

## Details
In the Linux kernel before 5.3.7, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/usb/misc/adutux.c driver, aka CID-44efc269db79.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=44efc269db7929f6275a1fa927ef082e533ecde0
