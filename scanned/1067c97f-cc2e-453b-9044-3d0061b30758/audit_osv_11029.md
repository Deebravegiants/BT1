# [M] CVE-2017-5667

## Summary
Severity: Medium
Advisory: CVE-2017-5667
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2017-5667
Type: osv

## Details
The sdhci_sdma_transfer_multi_blocks function in hw/sd/sdhci.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (out-of-bounds heap access and crash) or execute arbitrary code on the QEMU host via vectors involving the data transfer length.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commitdiff%3Bh=42922105beb14c2fc58185ea022b9f72fb5465e9
- http://www.securityfocus.com/bid/95885
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/01/30/2
- http://www.openwall.com/lists/oss-security/2017/01/31/10
- http://www.openwall.com/lists/oss-security/2017/02/12/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1417559
