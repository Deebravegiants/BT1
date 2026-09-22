# [M] CVE-2016-5337

## Summary
Severity: Medium
Advisory: CVE-2016-5337
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-14
Source: https://osv.dev/vulnerability/CVE-2016-5337
Type: osv

## Details
The megasas_ctrl_get_info function in hw/scsi/megasas.c in QEMU allows local guest OS administrators to obtain sensitive host memory information via vectors related to reading device control information.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=844864fbae66935951529408831c2f22367a57b6
- http://www.openwall.com/lists/oss-security/2016/06/08/13
- http://www.openwall.com/lists/oss-security/2016/06/08/3
- http://www.securityfocus.com/bid/91097
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-06/msg01969.html
