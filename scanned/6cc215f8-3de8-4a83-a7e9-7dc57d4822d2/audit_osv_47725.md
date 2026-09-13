# [C] CVE-2017-10915

## Summary
Severity: Critical
Advisory: CVE-2017-10915
CVSS: 9.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10915
Type: osv

## Details
The shadow-paging feature in Xen through 4.8.x mismanages page references and consequently introduces a race condition, which allows guest OS users to obtain Xen privileges, aka XSA-219.

## References
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/99174
- https://security.gentoo.org/glsa/201708-03
- https://security.gentoo.org/glsa/201710-17
- https://xenbits.xen.org/xsa/advisory-219.html
