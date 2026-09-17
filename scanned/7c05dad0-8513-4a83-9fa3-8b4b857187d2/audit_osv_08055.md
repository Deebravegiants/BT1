# [M] CVE-2016-10155

## Summary
Severity: Medium
Advisory: CVE-2016-10155
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10155
Type: osv

## Details
Memory leak in hw/watchdog/wdt_i6300esb.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (host memory consumption and QEMU process crash) via a large number of device unplug operations.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=eb7a20a3616085d46aa6b4b4224e15587ec67e6e
- http://www.securityfocus.com/bid/95770
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/01/20/14
- http://www.openwall.com/lists/oss-security/2017/01/21/4
