# [H] CVE-2017-10922

## Summary
Severity: High
Advisory: CVE-2017-10922
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10922
Type: osv

## Details
The grant-table feature in Xen through 4.8.x mishandles MMIO region grant references, which allows guest OS users to cause a denial of service (loss of grant trackability), aka XSA-224 bug 3.

## References
- http://www.securitytracker.com/id/1038734
- https://security.gentoo.org/glsa/201708-03
- https://security.gentoo.org/glsa/201710-17
- http://www.debian.org/security/2017/dsa-3969
- https://xenbits.xen.org/xsa/advisory-224.html
