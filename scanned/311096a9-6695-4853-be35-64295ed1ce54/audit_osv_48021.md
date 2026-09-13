# [H] CVE-2017-17045

## Summary
Severity: High
Advisory: CVE-2017-17045
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-11-28
Source: https://osv.dev/vulnerability/CVE-2017-17045
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing HVM guest OS users to gain privileges on the host OS, obtain sensitive information, or cause a denial of service (BUG and host OS crash) by leveraging the mishandling of Populate on Demand (PoD) Physical-to-Machine (P2M) errors.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00021.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00003.html
- https://security.gentoo.org/glsa/201801-14
- http://www.securityfocus.com/bid/102013
- http://www.securityfocus.com/bid/102129
- http://www.securitytracker.com/id/1039879
- https://support.citrix.com/article/CTX230138
- https://xenbits.xen.org/xsa/advisory-247.html
