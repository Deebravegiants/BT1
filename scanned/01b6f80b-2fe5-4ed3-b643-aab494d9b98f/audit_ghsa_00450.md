# [M] Apache Ranger allows remote authenticated administrators to inject arbitrary web script or HTML

## Summary
Severity: Medium
Advisory: GHSA-rf7q-xqm3-6923
CVE: CVE-2016-5395
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-rf7q-xqm3-6923
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0 <0.6.1

## Details
Cross-site scripting (XSS) vulnerability in the create user functionality in the policy admin tool in Apache Ranger before 0.6.1 allows remote authenticated administrators to inject arbitrary web script or HTML via vectors related to policies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5395
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://github.com/advisories/GHSA-rf7q-xqm3-6923
- http://www.securityfocus.com/bid/92577
