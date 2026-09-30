# [H] CVE-2015-8554

## Summary
Severity: High
Advisory: CVE-2015-8554
CVSS: 7.5 (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-04-14
Source: https://osv.dev/vulnerability/CVE-2015-8554
Type: osv

## Details
Buffer overflow in hw/pt-msi.c in Xen 4.6.x and earlier, when using the qemu-xen-traditional (aka qemu-dm) device model, allows local x86 HVM guest administrators to gain privileges by leveraging a system with access to a passed-through MSI-X capable physical PCI device and MSI-X table entries, related to a "write path."

## References
- http://support.citrix.com/article/CTX203879
- http://xenbits.xen.org/xsa/advisory-164.html
- https://security.gentoo.org/glsa/201604-03
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/79579
- http://www.securitytracker.com/id/1034481
