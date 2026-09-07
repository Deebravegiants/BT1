# [M] Missing permission check in Jenkins TestQuality Updater Plugin 

## Summary
Severity: Medium
Advisory: GHSA-xr8h-wj4v-rx7f
CVE: CVE-2023-24453
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-xr8h-wj4v-rx7f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:testquality-updater` — affected >=0

## Details
A missing check in Jenkins TestQuality Updater Plugin 1.3 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified username and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24453
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2800
