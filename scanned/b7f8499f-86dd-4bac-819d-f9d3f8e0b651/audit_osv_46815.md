# [M] CVE-2015-5158

## Summary
Severity: Medium
Advisory: CVE-2015-5158
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2015-5158
Type: osv

## Details
Stack-based buffer overflow in hw/scsi/scsi-bus.c in QEMU, when built with SCSI-device emulation support, allows guest OS users with CAP_SYS_RAWIO permissions to cause a denial of service (instance crash) via an invalid opcode in a SCSI command descriptor block.

## References
- http://www.securityfocus.com/bid/76016
- http://www.securitytracker.com/id/1033095
- https://lists.nongnu.org/archive/html/qemu-devel/2015-07/msg04558.html
- https://security.gentoo.org/glsa/201510-02
- https://lists.nongnu.org/archive/html/qemu-devel/2015-07/msg04558.html
