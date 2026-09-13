# [H] Jenkins Crap4J Plugin vulnerable to XML external entity (XXE) attacks

## Summary
Severity: High
Advisory: GHSA-vq5h-qgxm-2m39
CVE: CVE-2023-28680
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-vq5h-qgxm-2m39
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:crap4j` — affected >=0

## Details
Jenkins Crap4J Plugin 0.9 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control Crap Report file contents to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28680
- https://github.com/jenkinsci/crap4j-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2925
