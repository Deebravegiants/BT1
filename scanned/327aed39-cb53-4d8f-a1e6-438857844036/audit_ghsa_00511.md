# [C] The Admin UI in Apache Ranger before 0.5.1 does not properly handle authentication requests that lack a password

## Summary
Severity: Critical
Advisory: GHSA-j84c-j8qm-g47r
CVE: CVE-2016-0733
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-j84c-j8qm-g47r
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.5.1

## Details
The Admin UI in Apache Ranger before 0.5.1 does not properly handle authentication requests that lack a password, which allows remote attackers to bypass authentication by leveraging knowledge of a valid username.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0733
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-j84c-j8qm-g47r
- https://issues.apache.org/jira/browse/RANGER-835
- https://mail-archives.apache.org/mod_mbox/ranger-dev/201602.mbox/%3CD2D9A4C5.114ECA%25vel@apache.org%3E
- http://www.securityfocus.com/bid/82871
