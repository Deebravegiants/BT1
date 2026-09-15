# [H] Jenkins Performance Publisher Plugin vulnerable to XML external entity (XXE) attacks

## Summary
Severity: High
Advisory: GHSA-qgm7-m77f-j8pf
CVE: CVE-2023-28682
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-qgm7-m77f-j8pf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:perfpublisher` — affected >=0

## Details
Jenkins Performance Publisher Plugin 8.09 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control PerfPublisher report files to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28682
- https://github.com/jenkinsci/perfpublisher-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2928
