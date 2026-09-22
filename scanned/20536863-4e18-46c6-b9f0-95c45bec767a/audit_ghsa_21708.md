# [C] Apache Gobblin trusts all certificates used for LDAP connections in Gobblin-as-a-Service

## Summary
Severity: Critical
Advisory: GHSA-q5rx-8c2h-5q7j
CVE: CVE-2021-36152
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-06
Source: https://github.com/advisories/GHSA-q5rx-8c2h-5q7j
Type: github-advisory

## Affected
- Maven: `org.apache.gobblin:gobblin-core` — affected >=0 <0.16.0

## Details
Apache Gobblin trusts all certificates used for LDAP connections in Gobblin-as-a-Service. This affects versions <= 0.15.0. Users should update to version 0.16.0 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36152
- https://lists.apache.org/thread/3bxf7rbf4zh95r78jtgth6gwhr5fyl2j
