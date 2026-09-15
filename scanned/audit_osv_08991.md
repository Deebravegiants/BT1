# [M] CVE-2016-7157

## Summary
Severity: Medium
Advisory: CVE-2016-7157
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7157
Type: osv

## Details
The (1) mptsas_config_manufacturing_1 and (2) mptsas_config_ioc_0 functions in hw/scsi/mptconfig.c in QEMU (aka Quick Emulator) allow local guest OS administrators to cause a denial of service (QEMU process crash) via vectors involving MPTSAS_CONFIG_PACK.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=65a8e1f6413a0f6f79894da710b5d6d43361d27d
- http://www.openwall.com/lists/oss-security/2016/09/06/4
- http://www.openwall.com/lists/oss-security/2016/09/07/3
- http://www.securityfocus.com/bid/92775
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg04295.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg04296.html
