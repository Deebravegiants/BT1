# [H] Jenkins AbsInt a³ Plugin XML External Entity Reference vulnerability

## Summary
Severity: High
Advisory: GHSA-wf8m-qr47-xc9m
CVE: CVE-2023-28685
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-wf8m-qr47-xc9m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:absint-a3` — affected >=0

## Details
Jenkins AbsInt a³ Plugin 1.1.0 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control `Project File (APX)` contents to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28685
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2930
