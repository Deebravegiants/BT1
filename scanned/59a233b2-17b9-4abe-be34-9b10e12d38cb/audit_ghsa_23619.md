# [M] Reflected XSS vulnerability in Jenkins AWSEB Deployment Plugin

## Summary
Severity: Medium
Advisory: GHSA-f82v-pg74-6686
CVE: CVE-2020-2174
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f82v-pg74-6686
Type: github-advisory

## Affected
- Maven: `br.com.ingenieux.jenkins.plugins:awseb-deployment-plugin` — affected >=0 <0.3.20

## Details
AWSEB Deployment Plugin 0.3.19 and earlier does not escape various values printed as part of form validation output.

This results in a reflected cross-site scripting (XSS) vulnerability.

AWSEB Deployment Plugin 0.3.20 escapes the values printed as part of the affected form validation endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2174
- https://github.com/jenkinsci/awseb-deployment-plugin
- https://jenkins.io/security/advisory/2020-04-07/#SECURITY-1769
- http://www.openwall.com/lists/oss-security/2020/04/07/3
