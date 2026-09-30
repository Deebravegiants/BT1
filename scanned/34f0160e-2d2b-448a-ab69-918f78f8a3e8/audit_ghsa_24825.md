# [M] Jenkins JIRA Plugin allows users to select and use credentials with System scope

## Summary
Severity: Medium
Advisory: GHSA-98m4-m2c3-qxgq
CVE: CVE-2019-16541
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-98m4-m2c3-qxgq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira` — affected >=0 <3.0.11

## Details
Jenkins JIRA Plugin 3.0.10 and earlier does not declare the correct (folder) scope for per-folder Jira site definitions, allowing users to select and use credentials with System scope. Jira Plugin 3.0.11 defines the appropriate folder context for credential lookup. As a side effect, existing per-folder Jira sites may lose access to already configured System-scoped credentials, as if no credential was specified in the first place.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16541
- https://github.com/jenkinsci/jira-plugin/commit/3214a54b6871d82cb34a26949aad93b0fa78d1a8
- https://github.com/jenkinsci/jira-plugin
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1106
- http://www.openwall.com/lists/oss-security/2019/11/21/1
