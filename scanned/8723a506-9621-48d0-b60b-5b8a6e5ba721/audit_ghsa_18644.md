# [H] Apache Kylin Authentication Bypass Vulnerability

## Summary
Severity: High
Advisory: GHSA-mr9j-4j48-xcm2
CVE: CVE-2025-61733
CWE: CWE-288
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-mr9j-4j48-xcm2
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-core-common` — affected >=4.0.0 <5.0.3

## Details
Authentication Bypass Using an Alternate Path or Channel vulnerability in Apache Kylin.

This issue affects Apache Kylin: from 4.0.0 through 5.0.2.

Users are recommended to upgrade to version 5.0.3, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61733
- https://github.com/apache/kylin/pull/2336
- https://github.com/apache/kylin/commit/8b2cb8c71bd9885d70dad4f1a9822e38d9949b8c
- https://github.com/apache/kylin
- https://issues.apache.org/jira/browse/KYLIN-6081
- https://lists.apache.org/thread/8wmcffly6gp50nmfw8j4w3hlmv843yo0
- http://www.openwall.com/lists/oss-security/2025/09/30/7
