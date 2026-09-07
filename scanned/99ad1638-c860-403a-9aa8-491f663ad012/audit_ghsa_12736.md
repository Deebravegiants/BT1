# [H] Cross-site request forgery vulnerability in Jenkins BearyChat Plugin

## Summary
Severity: High
Advisory: GHSA-5xhh-6xfv-7q42
CVE: CVE-2023-24458
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-5xhh-6xfv-7q42
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bearychat` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins BearyChat Plugin 3.0.2 and earlier allows attackers to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24458
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2745
