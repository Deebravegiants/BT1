# [M] Apache XML Graphics FOP XML External Entity Reference ('XXE') vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jqfv-jrvq-95jm
CVE: CVE-2024-28168
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-09
Source: https://github.com/advisories/GHSA-jqfv-jrvq-95jm
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:fop-core` — affected >=0 <2.10

## Details
Improper Restriction of XML External Entity Reference ('XXE') vulnerability in Apache XML Graphics FOP.

This issue affects Apache XML Graphics FOP: 2.9.

Users are recommended to upgrade to version 2.10, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28168
- https://github.com/apache/xmlgraphics-fop/commit/d96ba9a11710d02716b6f4f6107ebfa9ccec7134
- https://github.com/apache/xmlgraphics-fop
- https://issues.apache.org/jira/browse/FOP-3168
- https://xmlgraphics.apache.org/security.html
- http://www.openwall.com/lists/oss-security/2024/10/09/1
