# [M] Jenkins Reverse Proxy Auth Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pmmr-r9v2-59p8
CVE: CVE-2023-32987
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-pmmr-r9v2-59p8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:reverse-proxy-auth-plugin` — affected >=0 <1.7.5

## Details
Jenkins Reverse Proxy Auth Plugin 1.7.4 and earlier does not require POST requests for a form validation method, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to connect to an attacker-specified LDAP server using attacker-specified credentials.

Reverse Proxy Auth Plugin 1.7.5 requires POST requests for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32987
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3002
