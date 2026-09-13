# [H] CVE-2017-16671

## Summary
Severity: High
Advisory: CVE-2017-16671
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-09
Source: https://osv.dev/vulnerability/CVE-2017-16671
Type: osv

## Details
A Buffer Overflow issue was discovered in Asterisk Open Source 13 before 13.18.1, 14 before 14.7.1, and 15 before 15.1.1 and Certified Asterisk 13.13 before 13.13-cert7. No size checking is done when setting the user field for Party B on a CDR. Thus, it is possible for someone to use an arbitrarily large string and write past the end of the user field storage buffer. NOTE: this is different from CVE-2017-7617, which was only about the Party A buffer.

## References
- http://downloads.digium.com/pub/security/AST-2017-010.html
- http://www.securityfocus.com/bid/101760
- https://security.gentoo.org/glsa/201811-11
- https://www.debian.org/security/2017/dsa-4076
- https://issues.asterisk.org/jira/browse/ASTERISK-27337
