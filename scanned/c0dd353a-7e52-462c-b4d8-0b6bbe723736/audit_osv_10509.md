# [M] CVE-2017-16672

## Summary
Severity: Medium
Advisory: CVE-2017-16672
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-09
Source: https://osv.dev/vulnerability/CVE-2017-16672
Type: osv

## Details
An issue was discovered in Asterisk Open Source 13 before 13.18.1, 14 before 14.7.1, and 15 before 15.1.1 and Certified Asterisk 13.13 before 13.13-cert7. A memory leak occurs when an Asterisk pjsip session object is created and that call gets rejected before the session itself is fully established. When this happens the session object never gets destroyed. Eventually Asterisk can run out of memory and crash.

## References
- http://downloads.digium.com/pub/security/AST-2017-011.html
- http://www.securityfocus.com/bid/101765
- https://issues.asterisk.org/jira/browse/ASTERISK-27345
- https://security.gentoo.org/glsa/201811-11
- https://www.debian.org/security/2017/dsa-4076
