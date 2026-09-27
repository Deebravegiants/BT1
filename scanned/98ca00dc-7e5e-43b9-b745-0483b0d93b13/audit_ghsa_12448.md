# [M] Apache StreamPark: Authenticated system users could trigger SQL injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rrcg-jwr5-32g7
CVE: CVE-2023-30867
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-rrcg-jwr5-32g7
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=2.0.0 <2.1.2

## Details
In the Streampark platform, when users log in to the system and use certain features, some pages provide a name-based fuzzy search, such as job names, role names, etc. The sql syntax :select * from table where jobName like '%jobName%'. However, the jobName field may receive illegal parameters, leading to SQL injection. This could potentially result in information leakage.

Mitigation:

Users are recommended to upgrade to version 2.1.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30867
- https://github.com/apache/incubator-streampark
- https://lists.apache.org/thread/bhdzh6hnh04yyf3g203bbyvxryd720o2
