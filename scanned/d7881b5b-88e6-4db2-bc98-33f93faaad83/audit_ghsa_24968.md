# [M] Jenkins Dynatrace Plugin contains Incorrect Default Permissions

## Summary
Severity: Medium
Advisory: GHSA-cqjv-whwg-wh47
CVE: CVE-2019-10463
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cqjv-whwg-wh47
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dynatrace-dashboard` — affected >=0 <2.1.5

## Details
A missing permission check in Jenkins Dynatrace Application Monitoring Plugin allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials. This issue was patched in version 2.1.5, however, please 

##NOTE: This plugin is marked as DEPRECATED

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10463
- https://github.com/jenkinsci/dynatrace-plugin/commit/b6e55709476d9f6dfaf75a4cd744fe1798868168
- https://github.com/jenkinsci/dynatrace-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1483%20(2)
- http://www.openwall.com/lists/oss-security/2019/10/23/2
