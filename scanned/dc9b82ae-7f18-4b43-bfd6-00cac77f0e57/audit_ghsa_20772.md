# [M] Jenkins Rundeck Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4jfq-4fqc-5j9c
CVE: CVE-2022-41233
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-4jfq-4fqc-5j9c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rundeck` — affected >=0 <3.6.12

## Details
Jenkins Rundeck Plugin 3.6.11 and earlier does not perform Run/Artifacts permission checks in multiple HTTP endpoints, allowing attackers with Item/Read permission to obtain information about build artifacts of a given job, if the optional Run/Artifacts permission is enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41233
- https://github.com/jenkinsci/rundeck-plugin/commit/032b3bb9eafee5f83e3ddeb023eb34d0eeae19b7
- https://github.com/jenkinsci/rundeck-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2170
