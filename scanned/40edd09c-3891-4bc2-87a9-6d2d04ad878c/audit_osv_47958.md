# [H] CVE-2017-15592

## Summary
Severity: High
Advisory: CVE-2017-15592
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15592
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing x86 HVM guest OS users to cause a denial of service (hypervisor crash) or possibly gain privileges because self-linear shadow mappings are mishandled for translated guests.

## References
- http://www.securityfocus.com/bid/102129
- https://support.citrix.com/article/CTX230138
- https://lists.debian.org/debian-lts-announce/2017/11/msg00027.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00021.html
- https://support.citrix.com/article/CTX228867
- https://security.gentoo.org/glsa/201801-14
- http://www.securityfocus.com/bid/101513
- http://www.securitytracker.com/id/1039568
- https://www.debian.org/security/2017/dsa-4050
- https://xenbits.xen.org/xsa/advisory-243.html
