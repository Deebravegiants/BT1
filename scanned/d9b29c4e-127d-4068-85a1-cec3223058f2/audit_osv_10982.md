# [M] CVE-2017-5526

## Summary
Severity: Medium
Advisory: CVE-2017-5526
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5526
Type: osv

## Details
Memory leak in hw/audio/es1370.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (host memory consumption and QEMU process crash) via a large number of device unplug operations.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=069eb7b2b8fc47c7cb52e5a4af23ea98d939e3da
- http://www.securityfocus.com/bid/95669
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.openwall.com/lists/oss-security/2017/01/18/1
- http://www.openwall.com/lists/oss-security/2017/01/18/8
