# [M] CVE-2016-9915

## Summary
Severity: Medium
Advisory: CVE-2016-9915
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-9915
Type: osv

## Details
Memory leak in hw/9pfs/9p-handle.c in QEMU (aka Quick Emulator) allows local privileged guest OS users to cause a denial of service (host memory consumption and possibly QEMU process crash) by leveraging a missing cleanup operation in the handle backend.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=971f406b77a6eb84e0ad27dcc416b663765aee30
- http://www.openwall.com/lists/oss-security/2016/12/06/11
- http://www.openwall.com/lists/oss-security/2016/12/08/7
- http://www.securityfocus.com/bid/94729
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201701-49
- https://lists.gnu.org/archive/html/qemu-devel/2016-11/msg03278.html
