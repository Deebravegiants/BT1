# [H] Jenkins Visual Studio Code Metrics Plugin vulnerable to XML external entity (XXE) attacks

## Summary
Severity: High
Advisory: GHSA-8j88-2hfc-5rf3
CVE: CVE-2023-28681
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-8j88-2hfc-5rf3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vs-code-metrics` — affected >=0

## Details
Jenkins Visual Studio Code Metrics Plugin 1.7 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control VS Code Metrics File contents to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28681
- https://github.com/jenkinsci/vs-code-metrics-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2926
