# [M] Apache Ranger policy engine incorrectly matches paths in certain conditions

## Summary
Severity: Medium
Advisory: GHSA-xv7x-x6wr-xx7g
CVE: CVE-2016-8746
CWE: CWE-426
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-xv7x-x6wr-xx7g
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger-plugins-common` — affected >=0 <0.6.3

## Details
Apache Ranger before 0.6.3 policy engine incorrectly matches paths in certain conditions when policy does not contain wildcards and has recursion flag set to true.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8746
- https://github.com/apache/ranger/commit/2fcd7f7cc175c0734443638b99c359e24c0f88ff
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-xv7x-x6wr-xx7g
- http://www.securityfocus.com/bid/95998
