# [M] CVE-2017-10919

## Summary
Severity: Medium
Advisory: CVE-2017-10919
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10919
Type: osv

## Details
Xen through 4.8.x mishandles virtual interrupt injection, which allows guest OS users to cause a denial of service (hypervisor crash), aka XSA-223.

## References
- http://www.securitytracker.com/id/1038733
- https://xenbits.xen.org/xsa/advisory-223.html
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/99159
- https://security.gentoo.org/glsa/201708-03
