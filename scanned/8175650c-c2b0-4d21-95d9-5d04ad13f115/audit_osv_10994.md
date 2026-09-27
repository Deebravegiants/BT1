# [M] CVE-2017-5579

## Summary
Severity: Medium
Advisory: CVE-2017-5579
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5579
Type: osv

## Details
Memory leak in the serial_exit_core function in hw/char/serial.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (host memory consumption and QEMU process crash) via a large number of device unplug operations.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=8409dc884a201bf74b30a9d232b6bbdd00cb7e2b
- http://www.securityfocus.com/bid/95780
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/01/24/8
- http://www.openwall.com/lists/oss-security/2017/01/25/3
