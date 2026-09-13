# [H] Apache Linkis vulnerable to privilege escalation

## Summary
Severity: High
Advisory: GHSA-v352-rg37-5q5m
CVE: CVE-2024-27181
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-v352-rg37-5q5m
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.6.0

## Details
In Apache Linkis <= 1.5.0, Privilege Escalation in Basic management services where the attacking user is a trusted account allows access to Linkis's Token information. Users are advised to upgrade to version 1.6.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27181
- https://github.com/apache/linkis
- https://lists.apache.org/thread/hosd73l7hxb3rpt5rb0yg0ld11zph4c6
- https://www.openwall.com/lists/oss-security/2024/08/02/3
