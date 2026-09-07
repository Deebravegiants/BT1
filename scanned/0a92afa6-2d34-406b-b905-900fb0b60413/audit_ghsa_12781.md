# [M] Plaintext Storage of a Password in Jenkins JIRA Pipeline Steps Plugin

## Summary
Severity: Medium
Advisory: GHSA-g29v-5pwh-wxx4
CVE: CVE-2023-24439
CWE: CWE-256, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-g29v-5pwh-wxx4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira-steps` — affected >=0

## Details
Jenkins JIRA Pipeline Steps Plugin 2.0.165.v8846cf59f3db and earlier stores the private keys unencrypted in its global configuration file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24439
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2774
