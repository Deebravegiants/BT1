# [M] Missing permission check in Jenkins RocketChat Notifier Plugin

## Summary
Severity: Medium
Advisory: GHSA-4p8f-2fwv-6xcw
CVE: CVE-2022-28139
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-4p8f-2fwv-6xcw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rocketchatnotifier` — affected >=0 <1.5.0

## Details
Jenkins RocketChat Notifier Plugin 1.4.10 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

RocketChat Notifier Plugin 1.5.0 requires POST requests and Overall/Administer permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28139
- https://github.com/jenkinsci/rocketchatnotifier-plugin/commit/1a0023be9f2e143434d028d5292ef9dc3195d051
- https://github.com/jenkinsci/rocketchatnotifier-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2241
- http://www.openwall.com/lists/oss-security/2022/03/29/1
