# [M] Apache Zeppelin: LDAP search filter query Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qmr3-52xf-wmhx
CVE: CVE-2024-31867
CWE: CWE-20, CWE-90
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-qmr3-52xf-wmhx
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-server` — affected >=0.8.2 <0.11.1

## Details
Improper Input Validation vulnerability in Apache Zeppelin.

The attackers can execute malicious queries by setting improper configuration properties to LDAP search filter.
This issue affects Apache Zeppelin: from 0.8.2 before 0.11.1.

Users are recommended to upgrade to version 0.11.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31867
- https://github.com/apache/zeppelin/pull/4714
- https://github.com/apache/zeppelin/commit/65d0bcc1ee8ec3ec372d0a71ab513cd20e6522a0
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/s4scw8bxdhrjs0kg0lhb68xqd8y9lrtf
- http://www.openwall.com/lists/oss-security/2024/04/09/12
