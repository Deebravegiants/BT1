# [H] CVE-2016-7426

## Summary
Severity: High
Advisory: CVE-2016-7426
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-7426
Type: osv

## Details
NTP before 4.2.8p9 rate limits responses received from the configured sources when rate limiting for all associations is enabled, which allows remote attackers to cause a denial of service (prevent responses from the sources) by sending responses with a spoofed source address.

## References
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:39.ntp.asc
- https://usn.ubuntu.com/3707-2/
- http://rhn.redhat.com/errata/RHSA-2017-0252.html
- http://www.securitytracker.com/id/1037354
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03706en_us
- https://www.kb.cert.org/vuls/id/633847
- http://nwtime.org/ntp428p9_release/
- http://support.ntp.org/bin/view/Main/SecurityNotice#Recent_Vulnerabilities
- http://www.securityfocus.com/bid/94451
- https://bto.bluecoat.com/security-advisory/sa139
- http://support.ntp.org/bin/view/Main/NtpBug3071
