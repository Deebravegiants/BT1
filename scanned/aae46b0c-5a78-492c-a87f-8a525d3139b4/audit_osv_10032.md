# [M] CVE-2017-12809

## Summary
Severity: Medium
Advisory: CVE-2017-12809
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-12809
Type: osv

## Details
QEMU (aka Quick Emulator), when built with the IDE disk and CD/DVD-ROM Emulator support, allows local guest OS privileged users to cause a denial of service (NULL pointer dereference and QEMU process crash) by flushing an empty CDROM device drive.

## References
- http://www.debian.org/security/2017/dsa-3991
- http://www.openwall.com/lists/oss-security/2017/08/21/2
- http://www.securityfocus.com/bid/100451
- https://lists.gnu.org/archive/html/qemu-devel/2017-08/msg01850.html
