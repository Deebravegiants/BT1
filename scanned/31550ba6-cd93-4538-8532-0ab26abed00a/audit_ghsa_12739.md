# [C] XML external entity reference vulnerability on agents in Jenkins Semantic Versioning Plugin 

## Summary
Severity: Critical
Advisory: GHSA-h8p8-6378-649p
CVE: CVE-2023-24430
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-h8p8-6378-649p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:semantic-versioning-plugin` — affected >=0 <1.15

## Details
Jenkins Semantic Versioning Plugin 1.14 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24430
- https://github.com/jenkinsci/semantic-versioning-plugin/commit/8df2fabd7d7396ae29c374914d1357744d3e454f
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2973%20(2)
