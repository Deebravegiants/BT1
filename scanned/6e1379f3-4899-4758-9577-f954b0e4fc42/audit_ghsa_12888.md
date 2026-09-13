# [M] Missing permissions check in Jenkins JIRA Pipeline Steps Plugin

## Summary
Severity: Medium
Advisory: GHSA-6j27-3xfw-cj2w
CVE: CVE-2023-24438
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-6j27-3xfw-cj2w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira-steps` — affected >=0

## Details
A missing permission check in Jenkins JIRA Pipeline Steps Plugin 2.0.165.v8846cf59f3db and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24438
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2786
