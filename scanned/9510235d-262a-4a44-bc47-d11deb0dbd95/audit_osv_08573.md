# [M] CVE-2016-4453

## Summary
Severity: Medium
Advisory: CVE-2016-4453
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-01
Source: https://osv.dev/vulnerability/CVE-2016-4453
Type: osv

## Details
The vmsvga_fifo_run function in hw/display/vmware_vga.c in QEMU allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) via a VGA command.

## References
- http://www.securityfocus.com/bid/90928
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1336650
- http://www.openwall.com/lists/oss-security/2016/05/30/2
- https://lists.gnu.org/archive/html/qemu-devel/2016-05/msg05270.html
