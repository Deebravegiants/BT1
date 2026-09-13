# [M] Arbitrary JSON and property file read vulnerability in Jenkins Extended Choice Parameter Plugin

## Summary
Severity: Medium
Advisory: GHSA-ch63-6cmg-gwg2
CVE: CVE-2022-27203
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-ch63-6cmg-gwg2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:extended-choice-parameter` — affected >=0

## Details
Jenkins Extended Choice Parameter Plugin 346.vd87693c5a_86c and earlier allows attackers with Item/Configure permission to read values from arbitrary JSON and Java properties files on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27203
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-1351
- http://www.openwall.com/lists/oss-security/2022/03/15/2
