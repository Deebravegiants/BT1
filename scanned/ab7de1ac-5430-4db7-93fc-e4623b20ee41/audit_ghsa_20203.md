# [M] Jenkins Jianliao Notification Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v6h8-5cp2-j9w4
CVE: CVE-2022-34206
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-v6h8-5cp2-j9w4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jianliao` — affected >=0

## Details
Jenkins Jianliao Notification Plugin 1.1 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to send HTTP POST requests to an attacker-specified URL.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34206
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2240
