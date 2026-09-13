# [M] CVE-2020-13754

## Summary
Severity: Medium
Advisory: CVE-2020-13754
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-02
Source: https://osv.dev/vulnerability/CVE-2020-13754
Type: osv

## Details
hw/pci/msix.c in QEMU 4.2.0 allows guest OS users to trigger an out-of-bounds access via a crafted address in an msi-x mmio operation.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00020.html
- https://security.gentoo.org/glsa/202011-09
- https://security.netapp.com/advisory/ntap-20200608-0007/
- https://usn.ubuntu.com/4467-1/
- https://www.debian.org/security/2020/dsa-4728
- http://www.openwall.com/lists/oss-security/2020/06/01/6
- http://www.openwall.com/lists/oss-security/2020/06/15/8
- https://lists.gnu.org/archive/html/qemu-devel/2020-06/msg00004.html
