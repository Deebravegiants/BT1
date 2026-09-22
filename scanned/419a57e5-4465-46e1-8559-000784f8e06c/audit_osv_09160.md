# [M] CVE-2016-8668

## Summary
Severity: Medium
Advisory: CVE-2016-8668
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8668
Type: osv

## Details
The rocker_io_writel function in hw/net/rocker/rocker.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (out-of-bounds read and QEMU process crash) by leveraging failure to limit DMA buffer size.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/15/9
- http://www.securityfocus.com/bid/93566
- https://security.gentoo.org/glsa/201611-11
- http://www.openwall.com/lists/oss-security/2016/10/14/8
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg02501.html
