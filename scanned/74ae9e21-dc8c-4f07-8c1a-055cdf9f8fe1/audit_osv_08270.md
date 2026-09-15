# [M] CVE-2016-2088

## Summary
Severity: Medium
Advisory: CVE-2016-2088
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-03-09
Source: https://osv.dev/vulnerability/CVE-2016-2088
Type: osv

## Details
resolver.c in named in ISC BIND 9.10.x before 9.10.3-P4, when DNS cookies are enabled, allows remote attackers to cause a denial of service (INSIST assertion failure and daemon exit) via a malformed packet with more than one cookie option.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181036.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178831.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179904.html
- http://www.securityfocus.com/bid/84290
- http://www.securitytracker.com/id/1035238
- https://kb.isc.org/article/AA-01380
- https://kb.isc.org/article/AA-01351
- https://security.gentoo.org/glsa/201610-07
