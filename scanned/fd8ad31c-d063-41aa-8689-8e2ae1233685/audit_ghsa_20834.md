# [M] CSRF vulnerability and mM

## Summary
Severity: Medium
Advisory: GHSA-p5hr-rf6w-3vvh
CVE: CVE-2022-41246
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-p5hr-rf6w-3vvh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ws-execution-manager` — affected >=0

## Details
Worksoft Execution Manager Plugin 10.0.3.503 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41246
- https://github.com/jenkinsci/ws-execution-manager-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2237
