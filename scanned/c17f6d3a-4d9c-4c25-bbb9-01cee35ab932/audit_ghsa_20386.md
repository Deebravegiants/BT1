# [M] Missing permission check in Jenkins Convertigo Mobile Platform Plugin

## Summary
Severity: Medium
Advisory: GHSA-7495-24mx-hph2
CVE: CVE-2022-34201
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-7495-24mx-hph2
Type: github-advisory

## Affected
- Maven: `com.convertigo.jenkins.plugins:convertigo-mobile-platform` — affected >=0

## Details
A missing permission check in Jenkins Convertigo Mobile Platform Plugin 1.1 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34201
- https://github.com/jenkinsci/convertigo-mobile-platform-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2276
