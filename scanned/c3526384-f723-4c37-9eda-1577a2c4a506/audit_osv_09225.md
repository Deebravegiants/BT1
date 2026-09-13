# [M] CVE-2016-9103

## Summary
Severity: Medium
Advisory: CVE-2016-9103
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-9103
Type: osv

## Details
The v9fs_xattrcreate function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS administrators to obtain sensitive host heap memory information by reading xattribute values before writing to them.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=eb687602853b4ae656e9236ee4222609f3a6887d
- http://www.openwall.com/lists/oss-security/2016/10/28/1
- http://www.openwall.com/lists/oss-security/2016/10/30/7
- http://www.securityfocus.com/bid/93955
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg01790.html
