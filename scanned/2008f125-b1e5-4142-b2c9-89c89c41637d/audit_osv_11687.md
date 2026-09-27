# [M] CVE-2017-9330

## Summary
Severity: Medium
Advisory: CVE-2017-9330
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2017-9330
Type: osv

## Details
QEMU (aka Quick Emulator) before 2.9.0, when built with the USB OHCI Emulation support, allows local guest OS users to cause a denial of service (infinite loop) by leveraging an incorrect return value, a different vulnerability than CVE-2017-6505.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=26f670a244982335cc08943fb1ec099a2c81e42d
- http://www.debian.org/security/2017/dsa-3920
- http://www.securityfocus.com/bid/98779
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/06/01/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1457697
