# [H] XXE vulnerability in Rundeck Plugin

## Summary
Severity: High
Advisory: GHSA-5xh7-6v3x-vrhj
CVE: CVE-2020-2144
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5xh7-6v3x-vrhj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rundeck` — affected >=0 <3.6.7

## Details
Rundeck Plugin 3.6.6 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows a user with Overall/Read access to have Jenkins parse a crafted HTTP request with XML data that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Rundeck Plugin 3.6.7 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2144
- https://github.com/jenkinsci/rundeck-plugin/commit/9222a2101d994b43b6c399630da978a4cf2ea62f
- https://github.com/jenkinsci/rundeck-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1702
- http://www.openwall.com/lists/oss-security/2020/03/09/1
