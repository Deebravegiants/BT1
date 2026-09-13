# [M] XXE vulnerability in Jenkins Subversion Plugin

## Summary
Severity: Medium
Advisory: GHSA-vp5f-8jgw-j53c
CVE: CVE-2020-2304
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vp5f-8jgw-j53c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:subversion` — affected >=0 <2.13.2

## Details
Jenkins Subversion Plugin 2.13.1 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control an agent process to have Jenkins parse a crafted changelog file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Subversion Plugin 2.13.2 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2304
- https://github.com/jenkinsci/subversion-plugin/commit/83f24081114a465f88d44fc84180d4d9d02c705d
- https://github.com/jenkinsci/subversion-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2145
- http://www.openwall.com/lists/oss-security/2020/11/04/6
