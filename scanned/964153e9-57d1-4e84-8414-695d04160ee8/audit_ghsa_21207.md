# [M] Incorrect Authorization in Jenkins Request Rename Or Delete Plugin

## Summary
Severity: Medium
Advisory: GHSA-qhmj-29vh-8mjm
CVE: CVE-2022-34814
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-qhmj-29vh-8mjm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rrod` — affected >=0

## Details
Jenkins Request Rename Or Delete Plugin 1.1.0 and earlier does not correctly perform a permission check in an HTTP endpoint, allowing attackers with Overall/Read permission to view an administrative configuration page listing pending requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34814
- https://github.com/jenkinsci/rrod-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-1996
