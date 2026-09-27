# [M] CVE-2016-9101

## Summary
Severity: Medium
Advisory: CVE-2016-9101
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-9101
Type: osv

## Details
Memory leak in hw/net/eepro100.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption and QEMU process crash) by repeatedly unplugging an i8255x (PRO100) NIC device.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.securityfocus.com/bid/93957
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201701-49
- http://www.openwall.com/lists/oss-security/2016/10/27/14
- http://www.openwall.com/lists/oss-security/2016/10/30/5
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg03024.html
