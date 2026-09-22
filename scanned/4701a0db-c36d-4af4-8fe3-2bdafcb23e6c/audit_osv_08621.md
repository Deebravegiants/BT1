# [M] CVE-2016-4964

## Summary
Severity: Medium
Advisory: CVE-2016-4964
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-4964
Type: osv

## Details
The mptsas_fetch_requests function in hw/scsi/mptsas.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop, and CPU consumption or QEMU process crash) via vectors involving s->state.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=06630554ccbdd25780aa03c3548aaff1eb56dffd
- http://www.openwall.com/lists/oss-security/2016/05/24/4
- http://www.openwall.com/lists/oss-security/2016/05/24/7
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-05/msg04027.html
