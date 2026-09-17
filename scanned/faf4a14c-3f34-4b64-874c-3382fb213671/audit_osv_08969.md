# [M] CVE-2016-7116

## Summary
Severity: Medium
Advisory: CVE-2016-7116
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7116
Type: osv

## Details
Directory traversal vulnerability in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS administrators to access host files outside the export path via a .. (dot dot) in an unspecified string.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=56f101ecce0eafd09e2daf1c4eeb1377d6959261
- http://www.openwall.com/lists/oss-security/2016/08/30/1
- http://www.openwall.com/lists/oss-security/2016/08/30/3
- http://www.securityfocus.com/bid/92680
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg03917.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg04231.html
- https://security.gentoo.org/glsa/201609-01
