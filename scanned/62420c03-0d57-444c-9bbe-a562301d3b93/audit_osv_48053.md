# [H] CVE-2017-17563

## Summary
Severity: High
Advisory: CVE-2017-17563
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/CVE-2017-17563
Type: osv

## Details
An issue was discovered in Xen through 4.9.x allowing guest OS users to cause a denial of service (host OS crash) or gain host OS privileges by leveraging an incorrect mask for reference-count overflow checking in shadow mode.

## References
- http://www.securityfocus.com/bid/102169
- http://www.securitytracker.com/id/1040769
- https://lists.debian.org/debian-lts-announce/2018/01/msg00003.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://support.citrix.com/article/CTX232096
- https://security.gentoo.org/glsa/201801-14
- https://www.debian.org/security/2018/dsa-4112
- https://xenbits.xen.org/xsa/advisory-249.html
- http://www.openwall.com/lists/oss-security/2017/12/12/2
