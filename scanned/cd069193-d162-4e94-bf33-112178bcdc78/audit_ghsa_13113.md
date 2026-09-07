# [H] Job Configuration History Plugin's path traversal allows exploiting XXE vulnerability

## Summary
Severity: High
Advisory: GHSA-ghjw-fcf6-rpr9
CVE: CVE-2023-41933
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-ghjw-fcf6-rpr9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jobConfigHistory` — affected >=0 <1229.v3039470161a_d

## Details
Jenkins Job Configuration History Plugin 1227.v7a_79fc4dc01f and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41933
- https://github.com/jenkinsci/job-config-history-plugin/commit/3039470161ada86f4091c75fc779ebfdb69f3210
- https://github.com/jenkinsci/job-config-history-plugin
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3235
- http://www.openwall.com/lists/oss-security/2023/09/06/9
