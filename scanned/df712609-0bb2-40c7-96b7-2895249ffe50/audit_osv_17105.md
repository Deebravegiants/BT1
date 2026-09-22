# [M] CVE-2020-12464

## Summary
Severity: Medium
Advisory: CVE-2020-12464
Aliases: A-156071259, ASB-A-156071259
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-29
Source: https://osv.dev/vulnerability/CVE-2020-12464
Type: osv

## Details
usb_sg_cancel in drivers/usb/core/message.c in the Linux kernel before 5.6.8 has a use-after-free because a transfer occurs without a reference, aka CID-056ad39ee925.

## References
- https://usn.ubuntu.com/4388-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://usn.ubuntu.com/4390-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.8
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4391-1/
- https://www.debian.org/security/2020/dsa-4699
- https://usn.ubuntu.com/4387-1/
- https://www.debian.org/security/2020/dsa-4698
- https://usn.ubuntu.com/4389-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://github.com/torvalds/linux/commit/056ad39ee9253873522f6469c3364964a322912b
- https://patchwork.kernel.org/patch/11463781/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=056ad39ee9253873522f6469c3364964a322912b
- https://lkml.org/lkml/2020/3/23/52
