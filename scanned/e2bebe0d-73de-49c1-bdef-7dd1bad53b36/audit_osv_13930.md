# [M] CVE-2018-5683

## Summary
Severity: Medium
Advisory: CVE-2018-5683
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2018-5683
Type: osv

## Details
The vga_draw_text function in Qemu allows local OS guest privileged users to cause a denial of service (out-of-bounds read and QEMU process crash) by leveraging improper memory address validation.

## References
- http://www.securityfocus.com/bid/102518
- https://access.redhat.com/errata/RHSA-2018:0816
- https://access.redhat.com/errata/RHSA-2018:1104
- https://access.redhat.com/errata/RHSA-2018:2162
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3575-1/
- https://www.debian.org/security/2018/dsa-4213
- http://www.openwall.com/lists/oss-security/2018/01/15/2
- https://lists.gnu.org/archive/html/qemu-devel/2018-01/msg02597.html
