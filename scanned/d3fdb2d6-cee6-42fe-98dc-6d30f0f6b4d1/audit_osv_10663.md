# [M] CVE-2017-18030

## Summary
Severity: Medium
Advisory: CVE-2017-18030
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-18030
Type: osv

## Details
The cirrus_invalidate_region function in hw/display/cirrus_vga.c in Qemu allows local OS guest privileged users to cause a denial of service (out-of-bounds array access and QEMU process crash) via vectors related to negative pitch.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=f153b563f8cf121aebf5a2fff5f0110faf58ccb3
- http://www.openwall.com/lists/oss-security/2018/01/15/3
- http://www.securityfocus.com/bid/102520
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
