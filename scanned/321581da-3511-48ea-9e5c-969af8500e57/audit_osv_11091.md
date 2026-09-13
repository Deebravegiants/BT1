# [M] CVE-2017-5987

## Summary
Severity: Medium
Advisory: CVE-2017-5987
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-5987
Type: osv

## Details
The sdhci_sdma_transfer_multi_blocks function in hw/sd/sdhci.c in QEMU (aka Quick Emulator) allows local OS guest privileged users to cause a denial of service (infinite loop and QEMU process crash) via vectors involving the transfer mode register during multi block transfer.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=6e86d90352adf6cb08295255220295cf23c4286e
- http://www.securityfocus.com/bid/96263
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201704-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1421995
- http://www.openwall.com/lists/oss-security/2017/02/14/8
- https://lists.gnu.org/archive/html/qemu-devel/2017-02/msg02776.html
