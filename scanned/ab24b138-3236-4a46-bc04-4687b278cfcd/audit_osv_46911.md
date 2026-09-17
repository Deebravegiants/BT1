# [M] CVE-2015-7975

## Summary
Severity: Medium
Advisory: CVE-2015-7975
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2015-7975
Type: osv

## Details
The nextvar function in NTP before 4.2.8p6 and 4.3.x before 4.3.90 does not properly validate the length of its input, which allows an attacker to cause a denial of service (application crash).

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00042.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00114.html
- http://support.ntp.org/bin/view/Main/NtpBug2937
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160127-ntpd
- http://www.securityfocus.com/bid/81959
- http://www.securitytracker.com/id/1034782
- http://www.ubuntu.com/usn/USN-3096-1
- https://bto.bluecoat.com/security-advisory/sa113
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:09.ntp.asc
- https://security.gentoo.org/glsa/201607-15
- https://security.netapp.com/advisory/ntap-20171031-0001/
- https://www.kb.cert.org/vuls/id/718152
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03750en_us
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03766en_us
