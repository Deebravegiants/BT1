# [M] CVE-2015-7549

## Summary
Severity: Medium
Advisory: CVE-2015-7549
CVSS: 6.0 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/CVE-2015-7549
Type: osv

## Details
The MSI-X MMIO support in hw/pci/msix.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (NULL pointer dereference and QEMU process crash) by leveraging failure to define the .write method.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175380.html
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/12/14/2
- http://www.securityfocus.com/bid/80761
- https://bugzilla.redhat.com/show_bug.cgi?id=1291137
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2015/12/14/2
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175380.html
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/12/14/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1291137
- https://security.gentoo.org/glsa/201602-01
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=43b11a91dd861a946b231b89b754285
