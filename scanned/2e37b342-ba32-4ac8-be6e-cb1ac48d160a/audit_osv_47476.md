# [H] CVE-2016-6258

## Summary
Severity: High
Advisory: CVE-2016-6258
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/CVE-2016-6258
Type: osv

## Details
The PV pagetable code in arch/x86/mm.c in Xen 4.7.x and earlier allows local 32-bit PV guest OS administrators to gain host OS privileges by leveraging fast-paths for updating pagetable entries.

## References
- http://www.securityfocus.com/bid/92131
- https://security.gentoo.org/glsa/201611-09
- http://www.debian.org/security/2016/dsa-3633
- http://www.securitytracker.com/id/1036446
- http://support.citrix.com/article/CTX214954
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://xenbits.xen.org/xsa/xsa182-4.5.patch
- http://xenbits.xen.org/xsa/xsa182-unstable.patch
- http://xenbits.xen.org/xsa/advisory-182.html
- http://xenbits.xen.org/xsa/xsa182-4.6.patch
