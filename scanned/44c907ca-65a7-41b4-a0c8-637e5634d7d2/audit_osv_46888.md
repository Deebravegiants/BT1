# [H] CVE-2015-7691

## Summary
Severity: High
Advisory: CVE-2015-7691
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2015-7691
Type: osv

## Details
The crypto_xmit function in ntpd in NTP 4.2.x before 4.2.8p4, and 4.3.x before 4.3.77 allows remote attackers to cause a denial of service (crash) via crafted packets containing particular autokey operations.  NOTE: This vulnerability exists due to an incomplete fix for CVE-2014-9750.

## References
- http://rhn.redhat.com/errata/RHSA-2016-0780.html
- http://rhn.redhat.com/errata/RHSA-2016-2583.html
- http://support.ntp.org/bin/view/Main/NtpBug2899
- http://www.debian.org/security/2015/dsa-3388
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/77274
- http://www.securitytracker.com/id/1033951
- https://bugzilla.redhat.com/show_bug.cgi?id=1274254
- https://security.gentoo.org/glsa/201607-15
- https://security.netapp.com/advisory/ntap-20171004-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1274254
