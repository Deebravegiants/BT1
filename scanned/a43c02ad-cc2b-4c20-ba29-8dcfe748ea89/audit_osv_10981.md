# [M] CVE-2017-5525

## Summary
Severity: Medium
Advisory: CVE-2017-5525
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5525
Type: osv

## Details
Memory leak in hw/audio/ac97.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (host memory consumption and QEMU process crash) via a large number of device unplug operations.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=12351a91da97b414eec8cdb09f1d9f41e535a401
- http://www.securityfocus.com/bid/95671
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/01/17/19
- http://www.openwall.com/lists/oss-security/2017/01/18/7
