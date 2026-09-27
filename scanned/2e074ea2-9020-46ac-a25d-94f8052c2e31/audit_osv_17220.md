# [M] CVE-2020-13800

## Summary
Severity: Medium
Advisory: CVE-2020-13800
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-13800
Type: osv

## Details
ati-vga in hw/display/ati.c in QEMU 4.2.0 allows guest OS users to trigger infinite recursion via a crafted mm_index value during an ati_mm_read or ati_mm_write call.

## References
- https://cve.openeuler.org/cve#/CVEInfo/CVE-2020-13800
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00086.html
- https://lists.gnu.org/archive/html/qemu-devel/2020-06/msg00825.html
- https://security.gentoo.org/glsa/202011-09
- https://security.netapp.com/advisory/ntap-20200717-0001/
- https://usn.ubuntu.com/4467-1/
- https://www.openwall.com/lists/oss-security/2020/06/04/2
