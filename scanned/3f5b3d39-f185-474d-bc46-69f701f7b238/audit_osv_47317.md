# [M] CVE-2016-2519

## Summary
Severity: Medium
Advisory: CVE-2016-2519
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-2519
Type: osv

## Details
ntpd in NTP before 4.2.8p7 and 4.3.x before 4.3.92 allows remote attackers to cause a denial of service (ntpd abort) by a large request data value, which triggers the ctl_getitem function to return a NULL value.

## References
- http://www.securitytracker.com/id/1035705
- https://www.kb.cert.org/vuls/id/718152
- http://support.ntp.org/bin/view/Main/NtpBug3008
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/88204
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:16.ntp.asc
- https://security.gentoo.org/glsa/201607-15
- https://security.netapp.com/advisory/ntap-20171004-0002/
