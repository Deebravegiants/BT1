# [M] CVE-2016-5105

## Summary
Severity: Medium
Advisory: CVE-2016-5105
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-02
Source: https://osv.dev/vulnerability/CVE-2016-5105
Type: osv

## Details
The megasas_dcmd_cfg_read function in hw/scsi/megasas.c in QEMU, when built with MegaRAID SAS 8708EM2 Host Bus Adapter emulation support, uses an uninitialized variable, which allows local guest administrators to read host memory via vectors involving a MegaRAID Firmware Interface (MFI) command.

## References
- http://www.openwall.com/lists/oss-security/2016/05/25/5
- http://www.openwall.com/lists/oss-security/2016/05/26/7
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1339583
- https://lists.gnu.org/archive/html/qemu-devel/2016-05/msg04419.html
