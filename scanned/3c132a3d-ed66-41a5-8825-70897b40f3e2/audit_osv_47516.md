# [H] CVE-2016-7434

## Summary
Severity: High
Advisory: CVE-2016-7434
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-7434
Type: osv

## Details
The read_mru_list function in NTP before 4.2.8p9 allows remote attackers to cause a denial of service (crash) via a crafted mrulist query.

## References
- http://nwtime.org/ntp428p9_release/
- http://support.ntp.org/bin/view/Main/SecurityNotice#Recent_Vulnerabilities
- http://www.securityfocus.com/bid/94448
- https://bto.bluecoat.com/security-advisory/sa139
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:39.ntp.asc
- http://www.securitytracker.com/id/1037354
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03706en_us
- https://www.kb.cert.org/vuls/id/633847
- http://support.ntp.org/bin/view/Main/NtpBug3082
- https://www.exploit-db.com/exploits/40806/
