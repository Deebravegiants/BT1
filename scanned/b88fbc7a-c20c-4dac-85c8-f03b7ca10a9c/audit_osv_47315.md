# [M] CVE-2016-2517

## Summary
Severity: Medium
Advisory: CVE-2016-2517
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-2517
Type: osv

## Details
NTP before 4.2.8p7 and 4.3.x before 4.3.92 allows remote attackers to cause a denial of service (prevent subsequent authentication) by leveraging knowledge of the controlkey or requestkey and sending a crafted packet to ntpd, which changes the value of trustedkey, controlkey, or requestkey.  NOTE: this vulnerability exists because of a CVE-2016-2516 regression.

## References
- http://www.securitytracker.com/id/1035705
- https://security.netapp.com/advisory/ntap-20171004-0002/
- https://www.kb.cert.org/vuls/id/718152
- http://support.ntp.org/bin/view/Main/NtpBug3010
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/88189
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:16.ntp.asc
- https://security.gentoo.org/glsa/201607-15
