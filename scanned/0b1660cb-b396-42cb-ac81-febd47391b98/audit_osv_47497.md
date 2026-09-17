# [H] CVE-2016-7092

## Summary
Severity: High
Advisory: CVE-2016-7092
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7092
Type: osv

## Details
The get_page_from_l3e function in arch/x86/mm.c in Xen allows local 32-bit PV guest OS administrators to gain host OS privileges via vectors related to L3 recursive pagetables.

## References
- http://support.citrix.com/article/CTX216071
- http://www.debian.org/security/2016/dsa-3663
- http://www.securityfocus.com/bid/92862
- http://www.securitytracker.com/id/1036751
- http://xenbits.xen.org/xsa/advisory-185.html
- http://xenbits.xen.org/xsa/xsa185.patch
- https://security.gentoo.org/glsa/201611-09
- http://xenbits.xen.org/xsa/advisory-185.html
- http://xenbits.xen.org/xsa/xsa185.patch
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
