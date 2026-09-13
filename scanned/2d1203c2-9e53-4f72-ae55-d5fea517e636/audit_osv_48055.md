# [M] CVE-2017-17565

## Summary
Severity: Medium
Advisory: CVE-2017-17565
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/CVE-2017-17565
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing PV guest OS users to cause a denial of service (host OS crash) if shadow mode and log-dirty mode are in place, because of an incorrect assertion related to M2P.

## References
- https://support.citrix.com/article/CTX232096
- http://www.securityfocus.com/bid/102175
- http://www.securitytracker.com/id/1040771
- https://lists.debian.org/debian-lts-announce/2018/01/msg00003.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://www.debian.org/security/2018/dsa-4112
- https://security.gentoo.org/glsa/201801-14
- https://xenbits.xen.org/xsa/advisory-251.html
- http://www.openwall.com/lists/oss-security/2017/12/12/5
