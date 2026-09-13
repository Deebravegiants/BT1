# [H] CVE-2016-5338

## Summary
Severity: High
Advisory: CVE-2016-5338
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-14
Source: https://osv.dev/vulnerability/CVE-2016-5338
Type: osv

## Details
The (1) esp_reg_read and (2) esp_reg_write functions in hw/scsi/esp.c in QEMU allow local guest OS administrators to cause a denial of service (QEMU process crash) or execute arbitrary code on the QEMU host via vectors related to the information transfer buffer.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=ff589551c8e8e9e95e211b9d8daafb4ed39f1aec
- http://www.openwall.com/lists/oss-security/2016/06/07/3
- http://www.openwall.com/lists/oss-security/2016/06/08/14
- http://www.securityfocus.com/bid/91079
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-06/msg01507.html
