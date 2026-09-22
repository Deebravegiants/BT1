# [M] CVE-2015-3420

## Summary
Severity: Medium
Advisory: CVE-2015-3420
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-19
Source: https://osv.dev/vulnerability/CVE-2015-3420
Type: osv

## Details
The ssl-proxy-openssl.c function in Dovecot before 2.2.17, when SSLv3 is disabled, allow remote attackers to cause a denial of service (login process crash) via vectors related to handshake failures.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-May/157030.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-May/158236.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-May/158261.html
- http://www.openwall.com/lists/oss-security/2015/04/27/1
- http://www.openwall.com/lists/oss-security/2015/04/28/4
- http://www.securityfocus.com/bid/74335
- https://bugzilla.redhat.com/show_bug.cgi?id=1216057
- https://dovecot.org/pipermail/dovecot-news/2015-May/000292.html
- https://dovecot.org/pipermail/dovecot/2015-April/100618.html
- http://www.openwall.com/lists/oss-security/2015/04/27/1
- http://www.openwall.com/lists/oss-security/2015/04/28/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1216057
