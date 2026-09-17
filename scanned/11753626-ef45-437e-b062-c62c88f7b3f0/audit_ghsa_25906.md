# [M] Passwords stored in plain text by Jenkins dbCharts Plugin

## Summary
Severity: Medium
Advisory: GHSA-x75r-g63m-82wj
CVE: CVE-2022-27216
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-x75r-g63m-82wj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dbCharts` — affected >=0

## Details
Jenkins dbCharts Plugin 0.5.2 and earlier stores JDBC connection passwords unencrypted in its global configuration file `hudson.plugins.dbcharts.DbChartPublisher.xml` on the Jenkins controller as part of its configuration.

These passwords can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27216
- https://github.com/jenkinsci/dbCharts-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2159
- http://www.openwall.com/lists/oss-security/2022/03/15/2
