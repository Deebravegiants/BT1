# [H] XML external entity (XXE) attacks in Jenkins Xcode integration Plugin

## Summary
Severity: High
Advisory: GHSA-wfxp-4qgw-qp3c
CVE: CVE-2021-21656
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-wfxp-4qgw-qp3c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xcode-plugin` — affected >=0 <2.0.15

## Details
Jenkins Xcode integration Plugin 2.0.14 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21656
- https://github.com/jenkinsci/xcode-plugin/commit/01335f1f4734e4a7eda69b28e182ecd4c34a1a4b
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2335
