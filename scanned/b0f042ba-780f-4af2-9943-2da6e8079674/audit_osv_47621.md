# [H] CVE-2016-9382

## Summary
Severity: High
Advisory: CVE-2016-9382
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9382
Type: osv

## Details
Xen 4.0.x through 4.7.x mishandle x86 task switches to VM86 mode, which allows local 32-bit x86 HVM guest OS users to gain privileges or cause a denial of service (guest OS crash) by leveraging a guest operating system that uses hardware task switching and allows a new task to start in VM86 mode.

## References
- https://security.gentoo.org/glsa/201612-56
- http://www.securityfocus.com/bid/94470
- http://www.securitytracker.com/id/1037341
- http://xenbits.xen.org/xsa/advisory-192.html
- https://support.citrix.com/article/CTX218775
