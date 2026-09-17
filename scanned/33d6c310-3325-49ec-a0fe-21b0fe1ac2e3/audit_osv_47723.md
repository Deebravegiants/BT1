# [C] CVE-2017-10913

## Summary
Severity: Critical
Advisory: CVE-2017-10913
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10913
Type: osv

## Details
The grant-table feature in Xen through 4.8.x provides false mapping information in certain cases of concurrent unmap calls, which allows backend attackers to obtain sensitive information or gain privileges, aka XSA-218 bug 1.

## References
- http://www.securitytracker.com/id/1038722
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/99411
- https://security.gentoo.org/glsa/201708-03
- https://security.gentoo.org/glsa/201710-17
- https://xenbits.xen.org/xsa/advisory-218.html
