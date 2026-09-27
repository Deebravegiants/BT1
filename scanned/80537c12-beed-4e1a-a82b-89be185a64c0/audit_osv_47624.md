# [H] CVE-2016-9386

## Summary
Severity: High
Advisory: CVE-2016-9386
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9386
Type: osv

## Details
The x86 emulator in Xen does not properly treat x86 NULL segments as unusable when accessing memory, which might allow local HVM guest users to gain privileges via vectors involving "unexpected" base/limit values.

## References
- https://security.gentoo.org/glsa/201612-56
- http://www.securityfocus.com/bid/94471
- http://www.securitytracker.com/id/1037340
- http://xenbits.xen.org/xsa/advisory-191.html
- https://support.citrix.com/article/CTX218775
