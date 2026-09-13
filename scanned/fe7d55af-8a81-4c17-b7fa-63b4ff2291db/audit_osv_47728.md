# [C] CVE-2017-10918

## Summary
Severity: Critical
Advisory: CVE-2017-10918
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10918
Type: osv

## Details
Xen through 4.8.x does not validate memory allocations during certain P2M operations, which allows guest OS users to obtain privileged host OS access, aka XSA-222.

## References
- http://www.securitytracker.com/id/1038732
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/99161
- https://security.gentoo.org/glsa/201708-03
- https://security.gentoo.org/glsa/201710-17
- https://xenbits.xen.org/xsa/advisory-222.html
