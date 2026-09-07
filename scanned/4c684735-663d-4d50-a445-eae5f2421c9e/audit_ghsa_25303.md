# [H] Stored XSS vulnerability in Jenkins Valgrind Plugin

## Summary
Severity: High
Advisory: GHSA-9hcr-66cj-r9hp
CVE: CVE-2020-2246
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9hcr-66cj-r9hp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:valgrind` — affected >=0

## Details
Jenkins Valgrind Plugin 0.28 and earlier does not escape content in Valgrind XML reports, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control Valgrind XML report contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2246
- https://github.com/jenkinsci/valgrind-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1830
- http://www.openwall.com/lists/oss-security/2020/09/01/3
