# [M] CVE-2016-9105

## Summary
Severity: Medium
Advisory: CVE-2016-9105
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-9105
Type: osv

## Details
Memory leak in the v9fs_link function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption) via vectors involving a reference to the source fid object.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=4c1586787ff43c9acd18a56c12d720e3e6be9f7c
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/28/3
- http://www.openwall.com/lists/oss-security/2016/10/30/9
- http://www.securityfocus.com/bid/93965
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg02608.html
