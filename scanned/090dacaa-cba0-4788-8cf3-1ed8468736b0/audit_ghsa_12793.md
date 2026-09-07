# [H] CSRF vulnerability in Jenkins TestQuality Updater Plugin 

## Summary
Severity: High
Advisory: GHSA-px2f-cqrf-f2qg
CVE: CVE-2023-24452
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-px2f-cqrf-f2qg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:testquality-updater` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins TestQuality Updater Plugin 1.3 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified username and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24452
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2800
