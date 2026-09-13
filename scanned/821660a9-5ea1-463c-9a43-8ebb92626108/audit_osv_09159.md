# [M] CVE-2016-8667

## Summary
Severity: Medium
Advisory: CVE-2016-8667
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8667
Type: osv

## Details
The rc4030_write function in hw/dma/rc4030.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (divide-by-zero error and QEMU process crash) via a large interval timer reload value.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/14/6
- http://www.openwall.com/lists/oss-security/2016/10/15/4
- http://www.securityfocus.com/bid/93567
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg02577.html
