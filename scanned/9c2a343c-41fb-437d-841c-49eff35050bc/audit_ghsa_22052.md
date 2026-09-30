# [M] Apache Wicket allows attackers to check for third-party libraries

## Summary
Severity: Medium
Advisory: GHSA-244g-8368-6wr9
CVE: CVE-2014-0043
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-244g-8368-6wr9
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-core` — affected >=1.5-RC1 <1.5.11
- Maven: `org.apache.wicket:wicket-core` — affected >=6.0.0-beta1 <6.14.0

## Details
In Apache Wicket 1.5.10 or 6.13.0, by issuing requests to special urls handled by Wicket, it is possible to check for the existence of particular classes in the classpath and thus check whether a third party library with a known security vulnerability is in use.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0043
- https://github.com/apache/wicket
- https://lists.apache.org/thread.html/d95e962f2f059a09f5abf7086c3f4ed22d2ae2c21499d0de95d4435d@1392986987@%3Cannounce.wicket.apache.org%3E
