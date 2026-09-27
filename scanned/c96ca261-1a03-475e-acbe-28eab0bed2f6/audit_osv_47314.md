# [M] CVE-2016-2516

## Summary
Severity: Medium
Advisory: CVE-2016-2516
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-2516
Type: osv

## Details
NTP before 4.2.8p7 and 4.3.x before 4.3.92, when mode7 is enabled, allows remote attackers to cause a denial of service (ntpd abort) by using the same IP address multiple times in an unconfig directive.

## References
- http://www.securitytracker.com/id/1035705
- http://support.ntp.org/bin/view/Main/NtpBug3011
- http://www.securityfocus.com/bid/88180
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:16.ntp.asc
- https://security.gentoo.org/glsa/201607-15
- https://www.kb.cert.org/vuls/id/718152
- http://www.debian.org/security/2016/dsa-3629
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- https://security.netapp.com/advisory/ntap-20171004-0002/
