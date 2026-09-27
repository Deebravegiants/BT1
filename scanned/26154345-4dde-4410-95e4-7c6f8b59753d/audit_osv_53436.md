# [H] CVE-2022-42335

## Summary
Severity: High
Advisory: CVE-2022-42335
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2022-42335
Type: osv

## Details
x86 shadow paging arbitrary pointer dereference In environments where host assisted address translation is necessary but Hardware Assisted Paging (HAP) is unavailable, Xen will run guests in so called shadow mode. Due to too lax a check in one of the hypervisor routines used for shadow page handling it is possible for a guest with a PCI device passed through to cause the hypervisor to access an arbitrary pointer partially under guest control.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PSPFWSY6UOPGMADQGOGN2PAAS5LJRPTG/
- http://www.openwall.com/lists/oss-security/2023/04/25/1
- https://security.gentoo.org/glsa/202402-07
- http://xenbits.xen.org/xsa/advisory-430.html
- https://xenbits.xenproject.org/xsa/advisory-430.txt
