# [H] Missing Authorization in Jenkins dbCharts Plugin

## Summary
Severity: High
Advisory: GHSA-m5wp-p3gj-7q5g
CVE: CVE-2022-25206
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-m5wp-p3gj-7q5g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dbCharts` — affected >=0

## Details
A missing check in Jenkins dbCharts Plugin 0.5.2 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified database via JDBC using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25206
- https://github.com/jenkinsci/dbCharts-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2177
