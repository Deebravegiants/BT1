# [M] CVE-2016-5106

## Summary
Severity: Medium
Advisory: CVE-2016-5106
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-09-02
Source: https://osv.dev/vulnerability/CVE-2016-5106
Type: osv

## Details
The megasas_dcmd_set_properties function in hw/scsi/megasas.c in QEMU, when built with MegaRAID SAS 8708EM2 Host Bus Adapter emulation support, allows local guest administrators to cause a denial of service (out-of-bounds write access) via vectors involving a MegaRAID Firmware Interface (MFI) command.

## References
- http://www.openwall.com/lists/oss-security/2016/05/25/6
- http://www.openwall.com/lists/oss-security/2016/05/26/8
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1339578
- https://lists.gnu.org/archive/html/qemu-devel/2016-05/msg04340.html
