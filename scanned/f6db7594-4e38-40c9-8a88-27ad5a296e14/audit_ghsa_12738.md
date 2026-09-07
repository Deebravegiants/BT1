# [H] CSRF vulnerability in Jenkins GitHub Pull Request Builder Plugin

## Summary
Severity: High
Advisory: GHSA-m6q8-mwf6-6mmc
CVE: CVE-2023-24434
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-m6q8-mwf6-6mmc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ghprb` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins GitHub Pull Request Builder Plugin 1.42.2 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24434
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2789%20(2)
