# [H] Jenkins jira-ext Plugin stores credentials unencrypted

## Summary
Severity: High
Advisory: GHSA-chm8-wp3h-f4m3
CVE: CVE-2019-10302
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-chm8-wp3h-f4m3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira-ext` — affected >=0 <0.9

## Details
Jenkins jira-ext Plugin 0.8 and earlier stored credentials unencrypted in its global configuration file `hudson.plugins.jira.JiraProjectProperty.xml` on the Jenkins master. These credentials could be viewed by users with access to the Jenkins master file system.

jira-ext Plugin version 0.9 stores credentials encrypted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10302
- https://github.com/jenkinsci/jira-ext-plugin/commit/e252f4084089e5cfb4c7bad389d3d20f3ec594fb
- https://jenkins.io/security/advisory/2019-04-17/#SECURITY-836
- http://www.securityfocus.com/bid/108045
