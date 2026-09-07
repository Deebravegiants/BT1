# [M] CSRF vulnerability in Jenkins Micro Focus Application Automation Tools Plugin

## Summary
Severity: Medium
Advisory: GHSA-mwg2-3xpv-5v28
CVE: CVE-2021-22512
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mwg2-3xpv-5v28
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:hp-application-automation-tools-plugin` — affected >=0 <6.8

## Details
Micro Focus Application Automation Tools Plugin 6.7 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to connect to attacker-specified URLs using attacker-specified username and password.

Additionally, these form validation methods do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Micro Focus Application Automation Tools Plugin 6.8 requires POST requests and Overall/Administer permission for the affected form validation methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22512
- https://github.com/jenkinsci/hpe-application-automation-tools-plugin/commit/497a143d9a95e9c937501ca329fe0dae22a0d9cd
- https://github.com/jenkinsci/hpe-application-automation-tools-plugin
- https://www.jenkins.io/security/advisory/2021-04-07/#SECURITY-2132
