# [M] Jenkins EasyQA Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-49j4-v37g-5gg2
CVE: CVE-2022-34204
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-49j4-v37g-5gg2
Type: github-advisory

## Affected
- Maven: `com.geteasyqa:easyqa` — affected >=0

## Details
Jenkins EasyQA Plugin 1.0 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified HTTP server.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34204
- https://github.com/jenkinsci/easyqa-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2281
