# [M] Jenkins buildgraph-view Plugin vulnerable to stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-4j4g-fp93-qvrw
CVE: CVE-2019-16562
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4j4g-fp93-qvrw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:buildgraph-view` — affected >=0

## Details
Jenkins buildgraph-view Plugin 1.8 and earlier does not escape the description of builds shown in its view, resulting in a stored cross-site scripting vulnerability exploitable by users able to change build descriptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16562
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1591
- http://www.openwall.com/lists/oss-security/2019/12/17/1
