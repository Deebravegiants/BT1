# [M] CVE-2018-12227

## Summary
Severity: Medium
Advisory: CVE-2018-12227
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12227
Type: osv

## Details
An issue was discovered in Asterisk Open Source 13.x before 13.21.1, 14.x before 14.7.7, and 15.x before 15.4.1 and Certified Asterisk 13.18-cert before 13.18-cert4 and 13.21-cert before 13.21-cert2. When endpoint specific ACL rules block a SIP request, they respond with a 403 forbidden. However, if an endpoint is not identified, then a 401 unauthorized response is sent. This vulnerability just discloses which requests hit a defined endpoint. The ACL rules cannot be bypassed to gain access to the disclosed endpoints.

## References
- http://downloads.asterisk.org/pub/security/AST-2018-008.html
- http://www.securityfocus.com/bid/104455
- https://security.gentoo.org/glsa/201811-11
- https://www.debian.org/security/2018/dsa-4320
- https://issues.asterisk.org/jira/browse/ASTERISK-27818
