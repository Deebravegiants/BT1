# [H] XXE vulnerability in Jenkins RapidDeploy Plugin

## Summary
Severity: High
Advisory: GHSA-g7w4-r4mg-gvhx
CVE: CVE-2020-2171
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g7w4-r4mg-gvhx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rapiddeploy-jenkins` — affected >=0 <4.2.1

## Details
RapidDeploy Plugin 4.2 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for the 'RapidDeploy deployment package build' build or post-build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller, server-side request forgery, or denial-of-service attacks.

RapidDeploy Plugin 4.2.1 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2171
- https://github.com/jenkinsci/rapiddeploy-plugin
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1677
- http://www.openwall.com/lists/oss-security/2020/03/25/2
