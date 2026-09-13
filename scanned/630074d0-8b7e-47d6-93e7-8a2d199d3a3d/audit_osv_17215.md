# [M] CVE-2020-13791

## Summary
Severity: Medium
Advisory: CVE-2020-13791
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-13791
Type: osv

## Details
hw/pci/pci.c in QEMU 4.2.0 allows guest OS users to trigger an out-of-bounds access by providing an address near the end of the PCI configuration space.

## References
- https://security.gentoo.org/glsa/202011-09
- https://security.netapp.com/advisory/ntap-20200717-0001/
- https://lists.gnu.org/archive/html/qemu-devel/2020-06/msg00706.html
- https://www.openwall.com/lists/oss-security/2020/06/04/1
