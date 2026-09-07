# [M] Stored XSS vulnerability in Jenkins ECharts API Plugin

## Summary
Severity: Medium
Advisory: GHSA-q397-w28f-jx97
CVE: CVE-2020-2194
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q397-w28f-jx97
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:echarts-api` — affected >=0 <4.7.0-4

## Details
ECharts API Plugin 4.7.0-3 and earlier does not escape the display name of the builds in the trend chart.

This results in a stored cross-site scripting (XSS) vulnerability that can be exploited by users with Run/Update permission.

ECharts API Plugin 4.7.0-4 escapes the display name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2194
- https://github.com/jenkinsci/echarts-api-plugin
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1842
- http://www.openwall.com/lists/oss-security/2020/06/03/3
