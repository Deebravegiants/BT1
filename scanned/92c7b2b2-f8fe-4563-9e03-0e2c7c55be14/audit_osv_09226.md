# [M] CVE-2016-9104

## Summary
Severity: Medium
Advisory: CVE-2016-9104
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-9104
Type: osv

## Details
Multiple integer overflows in the (1) v9fs_xattr_read and (2) v9fs_xattr_write functions in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allow local guest OS administrators to cause a denial of service (QEMU process crash) via a crafted offset, which triggers an out-of-bounds access.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/28/2
- http://www.openwall.com/lists/oss-security/2016/10/30/8
- http://www.securityfocus.com/bid/93956
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg02942.html
