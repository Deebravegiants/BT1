# [M] CVE-2016-7094

## Summary
Severity: Medium
Advisory: CVE-2016-7094
CVSS: 4.1 (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7094
Type: osv

## Details
Buffer overflow in Xen 4.7.x and earlier allows local x86 HVM guest OS administrators on guests running with shadow paging to cause a denial of service via a pagetable update.

## References
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/92864
- http://www.securitytracker.com/id/1036753
- https://security.gentoo.org/glsa/201611-09
- http://support.citrix.com/article/CTX216071
- http://www.debian.org/security/2016/dsa-3663
- http://xenbits.xen.org/xsa/advisory-187.html
- http://xenbits.xen.org/xsa/xsa187-0001-x86-shadow-Avoid-overflowing-sh_ctxt-seg_reg.patch
