# [M] Cleartext Transmission of Sensitive Information in Jenkins JIRA Pipeline Steps Plugin

## Summary
Severity: Medium
Advisory: GHSA-3g2g-rcm6-rrq2
CVE: CVE-2023-24440
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-3g2g-rcm6-rrq2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira-steps` — affected >=0

## Details
Jenkins JIRA Pipeline Steps Plugin 2.0.165.v8846cf59f3db and earlier transmits the private key in plain text as part of the global Jenkins configuration form, potentially resulting in their exposure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24440
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2774
