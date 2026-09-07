# [H] XXE vulnerability in FitNesse Plugin

## Summary
Severity: High
Advisory: GHSA-c3cg-mv5w-cvw8
CVE: CVE-2020-2120
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c3cg-mv5w-cvw8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fitnesse` — affected >=0 <1.31

## Details
FitNesse Plugin 1.30 and earlier does not configure the XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for its post-build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller, server-side request forgery, or denial-of-service attacks.

FitNesse Plugin 1.31 disables external entity processing for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2120
- https://github.com/jenkinsci/fitnesse-plugin/commit/7a913b9ff7e5a6acb0f4f4ec88d86da79db6af77
- https://github.com/jenkinsci/fitnesse-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1751
- http://www.openwall.com/lists/oss-security/2020/02/12/3
