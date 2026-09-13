# [C] XML Entity Expansion in Jenkins TestComplete support Plugin

## Summary
Severity: Critical
Advisory: GHSA-g5mj-c26g-vmpm
CVE: CVE-2023-24443
CWE: CWE-611, CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-g5mj-c26g-vmpm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:TestComplete` — affected >=0 <2.9

## Details
Jenkins TestComplete support Plugin 2.8.1 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24443
- https://github.com/jenkinsci/testcomplete-plugin/commit/971003ea578a090ed9a5b9487acb9d2aa93645d3
- https://github.com/jenkinsci/testcomplete-plugin/commit/cfb0fc3cd807cb72c24424cef98ce39710f2e5fb
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2741
