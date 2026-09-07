# [M] Missing permission check in Jenkins GitLab Plugin

## Summary
Severity: Medium
Advisory: GHSA-5phj-qv74-pv4w
CVE: CVE-2022-30955
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-5phj-qv74-pv4w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-plugin` — affected >=0 <1.5.32

## Details
Jenkins GitLab Plugin 1.5.31 and earlier does not perform a permission check in an HTTP endpoint, allowing attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. An enumeration of credentials IDs in GitLab Plugin 1.5.32 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30955
- https://github.com/jenkinsci/gitlab-plugin/commit/37e48ca920a4779109b885f4de62111e0baf846a
- https://github.com/jenkinsci/gitlab-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2753
