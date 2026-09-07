# [H] XXE vulnerability in NUnit Plugin

## Summary
Severity: High
Advisory: GHSA-xvhf-q744-5xm8
CVE: CVE-2020-2115
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xvhf-q744-5xm8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nunit` — affected >=0 <0.26

## Details
NUnit Plugin 0.25 and earlier does not configure the XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for its post-build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller, server-side request forgery, or denial-of-service attacks.

NUnit Plugin 0.26 disables external entity processing for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2115
- https://github.com/jenkinsci/nunit-plugin/commit/8f0b6a7b6a927c4b7003fdcd76862a3348b8205a
- https://github.com/jenkinsci/nunit-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1752
- http://www.openwall.com/lists/oss-security/2020/02/12/3
