# [M] Missing permission check in Jenkins AWS Global Configuration Plugin allows replacing plugin configuration

## Summary
Severity: Medium
Advisory: GHSA-7v7g-mh53-89hw
CVE: CVE-2020-2311
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7v7g-mh53-89hw
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:aws-global-configuration` — affected >=0 <1.6

## Details
Jenkins AWS Global Configuration Plugin 1.5 and earlier does not perform a permission check in an HTTP endpoint processing form submissions.

This allows attackers with Overall/Read permission to replace the global AWS configuration.

Jenkins AWS Global Configuration Plugin 1.6 properly performs permission checks when processing configuration form submissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2311
- https://github.com/jenkinsci/aws-global-configuration-plugin/commit/783618f98dcda35cee978c54ed8760b9436f5210
- https://github.com/jenkinsci/aws-global-configuration-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2101
