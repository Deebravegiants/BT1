# [H] CVE-2016-7093

## Summary
Severity: High
Advisory: CVE-2016-7093
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7093
Type: osv

## Details
Xen 4.5.3, 4.6.3, and 4.7.x allow local HVM guest OS administrators to overwrite hypervisor memory and consequently gain host OS privileges by leveraging mishandling of instruction pointer truncation during emulation.

## References
- http://www.securityfocus.com/bid/92865
- https://security.gentoo.org/glsa/201611-09
- http://support.citrix.com/article/CTX216071
- http://www.securitytracker.com/id/1036752
- http://xenbits.xen.org/xsa/xsa186-0001-x86-emulate-Correct-boundary-interactions-of-emulate.patch
- http://xenbits.xen.org/xsa/advisory-186.html
