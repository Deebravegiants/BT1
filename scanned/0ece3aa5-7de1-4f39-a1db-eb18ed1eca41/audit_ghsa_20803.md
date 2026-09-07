# [M] Missing permission check in Jenkins SCM HttpClient Plugin allow capturing credentials

## Summary
Severity: Medium
Advisory: GHSA-q9j5-2mjx-8x28
CVE: CVE-2022-41250
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-q9j5-2mjx-8x28
Type: github-advisory

## Affected
- Maven: `com.meowlomo.jenkins:scm-httpclient` — affected >=0

## Details
SCM HttpClient Plugin 1.5 and earlier does not perform permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified HTTP server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41250
- https://github.com/jenkinsci/scm-httpclient-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2708
- http://www.openwall.com/lists/oss-security/2022/09/21/5
