# [M] Path Traversal in Jenkins visualexpert Plugin

## Summary
Severity: Medium
Advisory: GHSA-8mmh-h4jh-2g34
CVE: CVE-2023-24455
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-8mmh-h4jh-2g34
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:visualexpert` — affected >=0

## Details
Jenkins visualexpert Plugin 1.3 and earlier does not restrict the names of files in methods implementing form validation, allowing attackers with Item/Configure permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24455
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2709
