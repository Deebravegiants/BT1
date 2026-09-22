# [M] CVE-2016-7156

## Summary
Severity: Medium
Advisory: CVE-2016-7156
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7156
Type: osv

## Details
The pvscsi_convert_sglist function in hw/scsi/vmw_pvscsi.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) by leveraging an incorrect cast.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=49adc5d3f8c6bb75e55ebfeab109c5c37dea65e8
- http://www.openwall.com/lists/oss-security/2016/09/06/3
- http://www.openwall.com/lists/oss-security/2016/09/07/2
- http://www.securityfocus.com/bid/92774
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg00772.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg01246.html
