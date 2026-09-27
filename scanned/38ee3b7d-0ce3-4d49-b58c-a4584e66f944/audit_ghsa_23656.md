# [H] XXE vulnerability in Jenkins URLTrigger Plugin

## Summary
Severity: High
Advisory: GHSA-34j5-c4cv-mmg5
CVE: CVE-2021-21659
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-34j5-c4cv-mmg5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:urltrigger` — affected >=0 <0.49

## Details
Jenkins URLTrigger Plugin 0.48 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with Job/Configure permission or otherwise able to control the contents of an URL to an XML document being examined for changes to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the polling Jenkins controller or agent, server-side request forgery, or denial-of-service attacks.

UJenkins RLTrigger Plugin 0.49 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21659
- https://github.com/jenkinsci/urltrigger-plugin
- https://www.jenkins.io/security/advisory/2021-05-25/#SECURITY-2341
- http://www.openwall.com/lists/oss-security/2021/05/25/3
