# [M] CVE-2016-8669

## Summary
Severity: Medium
Advisory: CVE-2016-8669
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8669
Type: osv

## Details
The serial_update_parameters function in hw/char/serial.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (divide-by-zero error and QEMU process crash) via vectors involving a value of divider greater than baud base.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=3592fe0c919cf27a81d8e9f9b4f269553418bb01
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/15/5
- http://www.securityfocus.com/bid/93563
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201611-11
- http://www.openwall.com/lists/oss-security/2016/10/14/9
