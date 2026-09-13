# [M] CVE-2017-9375

## Summary
Severity: Medium
Advisory: CVE-2017-9375
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-9375
Type: osv

## Details
QEMU (aka Quick Emulator), when built with USB xHCI controller emulator support, allows local guest OS privileged users to cause a denial of service (infinite recursive call) via vectors involving control transfer descriptors sequencing.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=96d87bdda3919bb16f754b3d3fd1227e1f38f13c
- http://www.debian.org/security/2017/dsa-3991
- http://www.securityfocus.com/bid/98915
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2019/09/msg00021.html
- http://www.openwall.com/lists/oss-security/2017/06/05/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1458744
