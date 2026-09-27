# [H] XXE vulnerability in Jenkins Filesystem Trigger Plugin

## Summary
Severity: High
Advisory: GHSA-cphv-7cxw-5hcc
CVE: CVE-2021-21657
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cphv-7cxw-5hcc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fstrigger` — affected >=0 <0.41

## Details
Jenkins Filesystem Trigger Plugin 0.40 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with Job/Configure permission or otherwise able to control the contents of an XML file being polled for changes to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the polling Jenkins controller or agent, server-side request forgery, or denial-of-service attacks.

Jenkins Filesystem Trigger Plugin 0.41 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21657
- https://github.com/jenkinsci/fstrigger-plugin
- https://www.jenkins.io/security/advisory/2021-05-25/#SECURITY-2339
- http://www.openwall.com/lists/oss-security/2021/05/25/3
