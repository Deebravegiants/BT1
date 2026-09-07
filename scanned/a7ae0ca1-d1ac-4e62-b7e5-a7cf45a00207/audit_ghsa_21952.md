# [H] CSRF vulnerability in Jenkins SCP publisher Plugin

## Summary
Severity: High
Advisory: GHSA-7g7g-82fp-hpxx
CVE: CVE-2022-25198
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-7g7g-82fp-hpxx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:scp` — affected >=0

## Details
SCP publisher Plugin 1.8 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified SSH server using attacker-specified credentials.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25198
- https://github.com/jenkinsci/scp-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2323
