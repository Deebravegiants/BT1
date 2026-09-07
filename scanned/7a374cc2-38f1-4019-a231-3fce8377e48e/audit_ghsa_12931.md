# [M] Cross-site request forgery vulnerability in Jenkins JIRA Pipeline Steps Plugin

## Summary
Severity: Medium
Advisory: GHSA-r3gm-jwf4-xgv2
CVE: CVE-2023-24437
CWE: CWE-352
Ecosystem: Maven
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-r3gm-jwf4-xgv2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira-steps` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins JIRA Pipeline Steps Plugin 2.0.165.v8846cf59f3db and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24437
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2786
