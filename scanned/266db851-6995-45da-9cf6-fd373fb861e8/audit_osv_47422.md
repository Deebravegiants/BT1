# [M] CVE-2016-5117

## Summary
Severity: Medium
Advisory: CVE-2016-5117
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-01-31
Source: https://osv.dev/vulnerability/CVE-2016-5117
Type: osv

## Details
OpenNTPD before 6.0p1 does not validate the CN for HTTPS constraint requests, which allows remote attackers to bypass the man-in-the-middle mitigations via a crafted timestamp constraint with a valid certificate.

## References
- http://www.openntpd.org/txt/release-6.0p1.txt
- http://www.openwall.com/lists/oss-security/2016/05/23/2
- http://www.openwall.com/lists/oss-security/2016/05/29/6
- http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.sbin/ntpd/constraint.c.diff?r1=1.27&r2=1.28
