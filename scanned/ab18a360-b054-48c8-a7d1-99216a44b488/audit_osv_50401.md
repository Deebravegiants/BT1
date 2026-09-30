# [M] CVE-2020-15393

## Summary
Severity: Medium
Advisory: CVE-2020-15393
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-29
Source: https://osv.dev/vulnerability/CVE-2020-15393
Type: osv

## Details
In the Linux kernel 4.4 through 5.7.6, usbtest_disconnect in drivers/usb/misc/usbtest.c has a memory leak, aka CID-28ebeb8db770.

## References
- https://lkml.org/lkml/2020/6/2/968
- https://usn.ubuntu.com/4463-1/
- https://usn.ubuntu.com/4465-1/
- https://usn.ubuntu.com/4485-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00071.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://usn.ubuntu.com/4483-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=28ebeb8db77035e058a510ce9bd17c2b9a009dba
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=831eebad70a25f55b5745453ac252d4afe997187
