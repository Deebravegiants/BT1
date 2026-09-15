# [M] CVE-2017-10923

## Summary
Severity: Medium
Advisory: CVE-2017-10923
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10923
Type: osv

## Details
Xen through 4.8.x does not validate a vCPU array index upon the sending of an SGI, which allows guest OS users to cause a denial of service (hypervisor crash), aka XSA-225.

## References
- http://www.securityfocus.com/bid/99160
- http://www.securitytracker.com/id/1038735
- https://security.gentoo.org/glsa/201708-03
- https://xenbits.xen.org/xsa/advisory-225.html
