# [M] Jenkins Code Dx Plugin missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-mjmf-7wjw-f5xx
CVE: CVE-2023-2631
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-mjmf-7wjw-f5xx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:codedx` — affected >=0 <4.0.0

## Details
Jenkins Code Dx Plugin 3.1.0 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Code Dx Plugin 4.0.0 requires POST requests and the appropriate permissions for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2631
- https://github.com/jenkinsci/codedx-plugin/commit/0214f30488ea8481f01e4b14a861e13d75bebb8b
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3118
