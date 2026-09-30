# [H] XXE vulnerability in Jenkins Klocwork Analysis Plugin

## Summary
Severity: High
Advisory: GHSA-p6c5-737r-2r93
CVE: CVE-2020-2247
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p6c5-737r-2r93
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:klocwork` — affected >=0 <2020.3.1

## Details
Klocwork Analysis Plugin 2020.2.1 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for the Klocwork plugin parser to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2247
- https://github.com/jenkinsci/klocwork-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1831
- http://www.openwall.com/lists/oss-security/2020/09/01/3
