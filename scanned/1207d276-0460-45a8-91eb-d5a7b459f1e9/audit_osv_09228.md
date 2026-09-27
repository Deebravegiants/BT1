# [M] CVE-2016-9106

## Summary
Severity: Medium
Advisory: CVE-2016-9106
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-9106
Type: osv

## Details
Memory leak in the v9fs_write function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption) by leveraging failure to free an IO vector.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=fdfcc9aeea1492f4b819a24c94dfb678145b1bf9
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/28/4
- http://www.openwall.com/lists/oss-security/2016/10/30/10
- http://www.securityfocus.com/bid/93964
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg02623.html
