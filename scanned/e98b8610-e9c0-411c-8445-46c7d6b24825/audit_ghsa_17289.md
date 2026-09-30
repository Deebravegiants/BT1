# [M] Jenkins Redpen - Pipeline Reporter for Jira Plugin has a path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qxh4-j39m-qfx4
CVE: CVE-2025-67643
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-qxh4-j39m-qfx4
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins:pipeline-reporter-by-redpen` — affected >=0

## Details
Jenkins Redpen - Pipeline Reporter for Jira Plugin 1.054.v7b_9517b_6b_202 and earlier does not correctly perform path validation of the workspace directory while uploading artifacts to Jira, allowing attackers with Item/Configure permission to retrieve files present on the Jenkins controller workspace directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67643
- https://github.com/jenkinsci/pipeline-reporter-by-redpen-plugin
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-3290
