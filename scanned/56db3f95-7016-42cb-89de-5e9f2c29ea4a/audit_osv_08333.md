# [M] CVE-2016-2316

## Summary
Severity: Medium
Advisory: CVE-2016-2316
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-22
Source: https://osv.dev/vulnerability/CVE-2016-2316
Type: osv

## Details
chan_sip in Asterisk Open Source 1.8.x, 11.x before 11.21.1, 12.x, and 13.x before 13.7.1 and Certified Asterisk 1.8.28, 11.6 before 11.6-cert12, and 13.1 before 13.1-cert3, when the timert1 sip.conf configuration is set to a value greater than 1245, allows remote attackers to cause a denial of service (file descriptor consumption) via vectors related to large retransmit timeout values.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177409.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177422.html
- http://www.debian.org/security/2016/dsa-3700
- http://www.securityfocus.com/bid/82651
- http://www.securitytracker.com/id/1034930
- http://downloads.asterisk.org/pub/security/AST-2016-002.html
