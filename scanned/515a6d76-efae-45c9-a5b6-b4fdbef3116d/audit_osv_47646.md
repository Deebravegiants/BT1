# [M] CVE-2016-9817

## Summary
Severity: Medium
Advisory: CVE-2016-9817
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/CVE-2016-9817
Type: osv

## Details
Xen through 4.7.x allows local ARM guest OS users to cause a denial of service (host crash) via vectors involving a (1) data or (2) prefetch abort with the ESR_EL2.EA bit set.

## References
- http://www.securitytracker.com/id/1037358
- https://security.gentoo.org/glsa/201612-56
- http://www.openwall.com/lists/oss-security/2016/11/29/3
- http://www.openwall.com/lists/oss-security/2016/12/05/7
- http://www.securityfocus.com/bid/94581
- http://xenbits.xen.org/xsa/advisory-201.html
- http://xenbits.xen.org/xsa/xsa201-3-4.7.patch
- http://xenbits.xen.org/xsa/xsa201-3.patch
