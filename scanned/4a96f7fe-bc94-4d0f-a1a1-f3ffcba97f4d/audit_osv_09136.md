# [M] CVE-2016-8577

## Summary
Severity: Medium
Advisory: CVE-2016-8577
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8577
Type: osv

## Details
Memory leak in the v9fs_read function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption) via vectors related to an I/O read operation.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=e95c9a493a5a8d6f969e86c9f19f80ffe6587e19
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/10/13
- http://www.securityfocus.com/bid/93473
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- http://www.openwall.com/lists/oss-security/2016/10/10/7
