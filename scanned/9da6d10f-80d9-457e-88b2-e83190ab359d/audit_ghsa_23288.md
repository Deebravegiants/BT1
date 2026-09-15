# [M] Missing permission check in Jenkins Rundeck Plugin

## Summary
Severity: Medium
Advisory: GHSA-p4f7-7c33-9675
CVE: CVE-2019-10455
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p4f7-7c33-9675
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rundeck` — affected >=0 <3.6.6

## Details
A missing permission check in Jenkins Rundeck Plugin allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10455
- https://github.com/jenkinsci/rundeck-plugin/commit/68177fc53f40d038233c9d54f3d59fdee9d6ced0
- https://github.com/jenkinsci/rundeck-plugin/commit/f0d115f14a9d2b0bfe4a33f1dc68aa637430b8ed
- https://github.com/jenkinsci/rundeck-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1460
