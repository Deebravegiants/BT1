# [M] Apache Ranger admin users can store some arbitrary javascript code to be executed when normal users login and access policies

## Summary
Severity: Medium
Advisory: GHSA-v7mf-qgxf-qmvf
CVE: CVE-2016-8751
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-v7mf-qgxf-qmvf
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.6.3

## Details
Apache Ranger before 0.6.is vulnerable to a Stored Cross-Site Scripting in when entering custom policy conditions. Admin users can store some arbitrary javascript code to be executed when normal users login and access policies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8751
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-v7mf-qgxf-qmvf
- http://www.securityfocus.com/bid/99067
