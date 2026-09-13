# [M] CVE-2017-9374

## Summary
Severity: Medium
Advisory: CVE-2017-9374
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-9374
Type: osv

## Details
Memory leak in QEMU (aka Quick Emulator), when built with USB EHCI Emulation support, allows local guest OS privileged users to cause a denial of service (memory consumption) by repeatedly hot-unplugging the device.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=d710e1e7bd3d5bfc26b631f02ae87901ebe646b0
- http://www.debian.org/security/2017/dsa-3920
- http://www.securityfocus.com/bid/98905
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.openwall.com/lists/oss-security/2017/06/06/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1459132
