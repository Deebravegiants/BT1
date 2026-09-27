# [H] CVE-2017-10914

## Summary
Severity: High
Advisory: CVE-2017-10914
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10914
Type: osv

## Details
The grant-table feature in Xen through 4.8.x has a race condition leading to a double free, which allows guest OS users to cause a denial of service (memory consumption), or possibly obtain sensitive information or gain privileges, aka XSA-218 bug 2.

## References
- http://www.securitytracker.com/id/1038722
- https://security.gentoo.org/glsa/201708-03
- https://security.gentoo.org/glsa/201710-17
- https://xenbits.xen.org/xsa/advisory-218.html
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/99411
