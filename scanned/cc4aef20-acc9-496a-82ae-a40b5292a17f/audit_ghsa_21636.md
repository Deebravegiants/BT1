# [M] Jenkins Snow Commander Plugin prior to 2.0 vulnerable to Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-2phq-ghf8-6586
CVE: CVE-2022-25193
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-2phq-ghf8-6586
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:embotics-vcommander` — affected >=0 <2.0

## Details
Snow Commander Plugin 1.10 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified webserver using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, these form validation methods do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25193
- https://github.com/jenkinsci/snowsoftware-commander-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2536
