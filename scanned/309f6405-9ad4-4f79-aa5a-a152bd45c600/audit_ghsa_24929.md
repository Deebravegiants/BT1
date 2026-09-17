# [M] Apache Geode gfsh query vulnerability

## Summary
Severity: Medium
Advisory: GHSA-37m3-qp37-x3c6
CVE: CVE-2017-9794
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-37m3-qp37-x3c6
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.2.1

## Details
When a cluster is operating in secure mode, a user with read privileges for specific data regions can use the gfsh command line utility to execute queries. In Apache Geode before 1.2.1, the query results may contain data from another user's concurrently executing gfsh query, potentially revealing data that the user is not authorized to view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9794
- https://issues.apache.org/jira/browse/GEODE-3217
- https://lists.apache.org/thread/403xxbfrh4csyj1st7351g2dkm0hb91v
