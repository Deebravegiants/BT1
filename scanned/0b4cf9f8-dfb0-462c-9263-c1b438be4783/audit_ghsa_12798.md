# [M] Plaintext storage of Access Token in Jenkins GitHub Pull Request Coverage Status Plugin

## Summary
Severity: Medium
Advisory: GHSA-4x65-4fjx-r7m6
CVE: CVE-2023-24442
CWE: CWE-256, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-4x65-4fjx-r7m6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:github-pr-coverage-status` — affected >=0

## Details
Jenkins GitHub Pull Request Coverage Status Plugin 2.2.0 and earlier stores the GitHub Personal Access Token, Sonar access token and Sonar password unencrypted in its global configuration file on the Jenkins controller where they can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24442
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2767
