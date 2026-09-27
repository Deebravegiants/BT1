# [M] CVE-2015-8613

## Summary
Severity: Medium
Advisory: CVE-2015-8613
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2015-8613
Type: osv

## Details
Stack-based buffer overflow in the megasas_ctrl_get_info function in QEMU, when built with SCSI MegaRAID SAS HBA emulation support, allows local guest users to cause a denial of service (QEMU instance crash) via a crafted SCSI controller CTRL_GET_INFO command.

## References
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/12/22/1
- http://www.securityfocus.com/bid/79719
- https://bugzilla.redhat.com/show_bug.cgi?id=1284008
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg03737.html
- https://security.gentoo.org/glsa/201604-01
- http://www.openwall.com/lists/oss-security/2015/12/22/1
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg03737.html
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg03737.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1284008
