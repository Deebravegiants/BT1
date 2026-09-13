# [M] CVE-2016-4454

## Summary
Severity: Medium
Advisory: CVE-2016-4454
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-06-01
Source: https://osv.dev/vulnerability/CVE-2016-4454
Type: osv

## Details
The vmsvga_fifo_read_raw function in hw/display/vmware_vga.c in QEMU allows local guest OS administrators to obtain sensitive host memory information or cause a denial of service (QEMU process crash) by changing FIFO registers and issuing a VGA command, which triggers an out-of-bounds read.

## References
- http://www.openwall.com/lists/oss-security/2016/05/30/3
- http://www.securityfocus.com/bid/90927
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1336429
- https://lists.gnu.org/archive/html/qemu-devel/2016-05/msg05271.html
