# [H] Cross-Site Request Forgery in Jenkins dbCharts Plugin

## Summary
Severity: High
Advisory: GHSA-vx6f-6rp6-f2px
CVE: CVE-2022-25205
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-vx6f-6rp6-f2px
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dbCharts` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins dbCharts Plugin 0.5.2 and earlier allows attackers to connect to an attacker-specified database via JDBC using attacker-specified credentials and to determine if a class is available in the Jenkins instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25205
- https://github.com/jenkinsci/dbCharts-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2177
